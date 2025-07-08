#!/usr/bin/env python3
"""
Manga Metadata Tool

A tool to create ComicInfo.xml files for manga using the AniList API.
"""

import click
import zipfile
from pathlib import Path
from src.anilist_client import AniListClient
from src.comicinfo_generator import ComicInfoGenerator


@click.group()
def cli():
    """Manga Metadata Tool - Create ComicInfo.xml files using AniList API."""
    pass


@cli.command()
@click.argument('query', type=str)
@click.option('--limit', '-l', default=10, help='Number of search results to show (default: 10)')
def search(query: str, limit: int):
    """Search for manga on AniList."""
    client = AniListClient()

    click.echo(f"Searching for: {query}")
    click.echo("-" * 50)

    try:
        results = client.search_manga(query, limit)

        if not results:
            click.echo("No results found.")
            return

        for i, manga in enumerate(results, 1):
            click.echo(f"{i}. {manga.title_romaji}")
            if manga.title_english and manga.title_english != manga.title_romaji:
                click.echo(f"   English: {manga.title_english}")
            if manga.title_native:
                click.echo(f"   Native: {manga.title_native}")
            click.echo(f"   ID: {manga.id}")
            click.echo(f"   Status: {manga.status}")
            if manga.start_date:
                click.echo(f"   Start Date: {manga.start_date}")
            if manga.chapters:
                click.echo(f"   Chapters: {manga.chapters}")
            if manga.volumes:
                click.echo(f"   Volumes: {manga.volumes}")
            click.echo()

    except Exception as e:
        click.echo(f"Error searching: {e}", err=True)


@cli.command()
@click.argument('manga_id', type=int)
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: ComicInfo.xml)')
@click.option('--volume', '-v', type=int, help='Volume number')
@click.option('--chapter', '-c', type=str, help='Chapter number')
@click.option('--scan-info', '-s', type=str, help='Scan information (e.g., scanlator name)')
def generate(manga_id: int, output: str, volume: int, chapter: str, scan_info: str):
    """Generate ComicInfo.xml for a specific manga."""
    client = AniListClient()
    generator = ComicInfoGenerator()

    try:
        # Get detailed manga information
        click.echo(f"Fetching manga details for ID: {manga_id}")
        manga = client.get_manga_details(manga_id)

        if not manga:
            click.echo("Manga not found.", err=True)
            return

        click.echo(f"Found: {manga.title_romaji}")

        # Generate ComicInfo.xml
        comic_info = generator.generate_comic_info(manga=manga, volume=volume, chapter=chapter, scan_info=scan_info)

        # Determine output path
        if not output:
            output = "ComicInfo.xml"

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write XML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(comic_info)

        click.echo(f"ComicInfo.xml generated successfully: {output_path}")

    except Exception as e:
        click.echo(f"Error generating ComicInfo.xml: {e}", err=True)


@cli.command()
@click.argument('query', type=str)
@click.option('--output-dir', '-d', type=click.Path(), default='./output', help='Output directory')
@click.option('--volumes', type=str, help='Volume range (e.g., 1-5 or 1,3,5)')
def batch(query: str, output_dir: str, volumes: str):
    """Generate ComicInfo.xml files for multiple volumes of a manga series."""
    client = AniListClient()
    generator = ComicInfoGenerator()

    try:
        # Search for manga
        results = client.search_manga(query, limit=1)
        if not results:
            click.echo("No manga found.", err=True)
            return

        manga = client.get_manga_details(results[0].id)
        if not manga:
            click.echo("Failed to get manga details.", err=True)
            return

        click.echo(f"Processing: {manga.title_romaji}")

        # Parse volume range
        volume_list = []
        if volumes:
            if '-' in volumes:
                start, end = map(int, volumes.split('-'))
                volume_list = list(range(start, end + 1))
            else:
                volume_list = [int(v.strip()) for v in volumes.split(',')]
        else:
            # Default to all volumes if available
            if manga.volumes:
                volume_list = list(range(1, manga.volumes + 1))
            else:
                volume_list = [1]  # Default to volume 1

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate ComicInfo.xml for each volume
        for volume in volume_list:
            comic_info = generator.generate_comic_info(manga=manga, volume=volume)

            filename = f"ComicInfo_Vol{volume:02d}.xml"
            file_path = output_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(comic_info)

            click.echo(f"Generated: {file_path}")

        click.echo(f"\nAll files generated in: {output_path}")

    except Exception as e:
        click.echo(f"Error in batch generation: {e}", err=True)


def _add_comicinfo_to_cbz(cbz_path: Path, comicinfo_content: str) -> bool:
    """Add ComicInfo.xml content to a CBZ file."""
    try:
        # Create a temporary file
        temp_path = cbz_path.with_suffix('.cbz.tmp')

        # Create new CBZ with ComicInfo.xml
        with zipfile.ZipFile(cbz_path, 'r') as original_zip:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy all existing files
                for item in original_zip.infolist():
                    if item.filename != 'ComicInfo.xml':  # Skip existing ComicInfo.xml if present
                        data = original_zip.read(item.filename)
                        new_zip.writestr(item, data)

                # Add the new ComicInfo.xml
                new_zip.writestr('ComicInfo.xml', comicinfo_content.encode('utf-8'))

        # Replace original with modified version
        temp_path.replace(cbz_path)
        return True

    except Exception as e:
        click.echo(f"❌ Error processing {cbz_path.name}: {e}", err=True)
        if temp_path.exists():
            temp_path.unlink()
        return False


@cli.command()
@click.argument('cbz_dir', type=click.Path(exists=True, path_type=Path))
@click.argument('manga_id', type=int)
@click.option('--metadata-type', '-t', type=click.Choice(['chapters', 'volumes']), default='chapters',
              help='Type of metadata to generate (chapters or volumes)')
@click.option('--pattern', '-p', type=str,
              help='CBZ filename pattern (e.g., "c{:03d}.cbz" for c001.cbz, c002.cbz)')
@click.option('--range', '-r', 'range_spec', type=str,
              help='Range of chapters/volumes (e.g., "1-10" or "1,3,5-8")')
@click.option('--scan-info', '-s', type=str, help='Scan information to add to metadata')
@click.option('--dry-run', is_flag=True, help='Show what would be processed without making changes')
def embed(cbz_dir: Path, manga_id: int, metadata_type: str, pattern: str, range_spec: str, scan_info: str, dry_run: bool):
    """Embed ComicInfo.xml metadata directly into CBZ files.

    CBZ_DIR: Directory containing CBZ files
    MANGA_ID: AniList manga ID
    """
    client = AniListClient()
    generator = ComicInfoGenerator()

    try:
        # Get manga details
        click.echo(f"Fetching manga details for ID: {manga_id}")
        manga = client.get_manga_details(manga_id)

        if not manga:
            click.echo("Manga not found.", err=True)
            return

        click.echo(f"Found: {manga.title_romaji}")

        # Parse range
        numbers = []
        if range_spec:
            if '-' in range_spec:
                start, end = map(int, range_spec.split('-'))
                numbers = list(range(start, end + 1))
            else:
                numbers = [int(x.strip()) for x in range_spec.split(',')]
        else:
            # Auto-detect from directory
            if metadata_type == 'volumes' and manga.volumes:
                numbers = list(range(1, manga.volumes + 1))
            else:
                # Try to find CBZ files and extract numbers
                cbz_files = list(cbz_dir.glob('*.cbz'))
                click.echo(f"Found {len(cbz_files)} CBZ files in directory")
                if not cbz_files:
                    click.echo("No CBZ files found in directory.", err=True)
                    return
                # For auto-detection, we'll process files as we find them
                numbers = list(range(1, len(cbz_files) + 1))

        # Determine filename pattern
        if not pattern:
            if metadata_type == 'chapters':
                pattern = 'c{:03d}.cbz'  # c001.cbz, c002.cbz, etc.
            else:
                pattern = 'v{:02d}.cbz'   # v01.cbz, v02.cbz, etc.

        click.echo(f"Processing {metadata_type} with pattern: {pattern}")
        if dry_run:
            click.echo("DRY RUN - No files will be modified")
        click.echo()

        success_count = 0
        total_count = 0

        for number in numbers:
            total_count += 1

            # Handle decimal numbers (like 7.5)
            if '.' in str(number):
                filename = pattern.replace('{:03d}', str(number)).replace('{:02d}', str(number))
            else:
                try:
                    filename = pattern.format(int(number))
                except (ValueError, TypeError):
                    filename = pattern.replace('{:03d}', str(number)).replace('{:02d}', str(number))

            cbz_path = cbz_dir / filename

            if not cbz_path.exists():
                click.echo(f"⚠️  CBZ file not found: {filename}")
                continue

            # Generate metadata
            if metadata_type == 'chapters':
                comic_info = generator.generate_comic_info(
                    manga=manga,
                    chapter=str(number),
                    scan_info=scan_info
                )
            else:
                comic_info = generator.generate_comic_info(
                    manga=manga,
                    volume=int(number),
                    scan_info=scan_info
                )

            if dry_run:
                click.echo(f"📄 Would process: {filename}")
                continue

            # Add metadata to CBZ
            if _add_comicinfo_to_cbz(cbz_path, comic_info):
                click.echo(f"✅ Added ComicInfo.xml to {filename}")
                success_count += 1

        click.echo()
        if dry_run:
            click.echo(f"📊 Would process: {total_count} files")
        else:
            click.echo(f"📊 Results: {success_count}/{total_count} files processed successfully")

            if success_count == total_count and success_count > 0:
                click.echo("🎉 All files processed! Your CBZ files now contain ComicInfo.xml metadata.")
                click.echo()
                click.echo("📖 For Komga/Kavita:")
                click.echo("   1. Refresh your library")
                click.echo("   2. The metadata should now be automatically recognized")
                click.echo("   3. Series info, chapter numbers, and other details will be displayed")

    except Exception as e:
        click.echo(f"Error in embed operation: {e}", err=True)


def main():
    """Entry point for the application."""
    cli()


if __name__ == "__main__":
    main()
