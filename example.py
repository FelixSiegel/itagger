#!/usr/bin/env python3
"""
Example script showing how to use the manga metadata tool.
"""

from typing import Optional
from manga_tagger.anilist_client import AniListClient
from manga_tagger.comicinfo_generator import ComicInfoGenerator
from manga_tagger.models import MangaDetails


def main():
    """Example usage of the manga metadata tool."""
    client = AniListClient()
    generator = ComicInfoGenerator()

    # Example 1: Search for manga
    print("=== Searching for 'One Piece' ===")
    try:
        results = client.search_manga("One Piece", limit=3)
        for i, search_result in enumerate(results, 1):
            print(f"{i}. {search_result.title_romaji} (ID: {search_result.id})")
            if search_result.title_english:
                print(f"   English: {search_result.title_english}")
            print(f"   Status: {search_result.status}")
            print(f"   Volumes: {search_result.volumes}")
            print()
    except Exception as e:
        print(f"Search error: {e}")

    # Example 2: Get detailed information and generate ComicInfo.xml
    print("=== Generating ComicInfo.xml for a specific manga ===")
    try:
        # Using a well-known manga ID (you can replace this with any valid ID)
        manga_id = 30013  # One Piece
        manga_details: Optional[MangaDetails] = client.get_manga_details(manga_id)

        if manga_details:
            print(f"Retrieved details for: {manga_details.title_romaji}")
            print(f"Authors: {', '.join(manga_details.get_authors())}")
            print(f"Artists: {', '.join(manga_details.get_artists())}")
            print(f"Genres: {', '.join(manga_details.genres or [])}")

            # Generate ComicInfo.xml for volume 1
            comic_info = generator.generate_comic_info(manga=manga_details, volume=1, scan_info="Example Scanlation Group")

            # Save to file
            with open("example_ComicInfo.xml", "w", encoding="utf-8") as f:
                f.write(comic_info)

            print("ComicInfo.xml generated successfully: example_ComicInfo.xml")
        else:
            print("Manga not found")
    except Exception as e:
        print(f"Generation error: {e}")


if __name__ == "__main__":
    main()
