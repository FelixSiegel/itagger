"""ComicInfo.xml generator for manga metadata."""

import html
from typing import Optional
from lxml import etree
from .models import MangaDetails, ComicInfoData


class ComicInfoGenerator:
    """Generator for ComicInfo.xml files based on manga metadata."""

    def __init__(self):
        self.namespace = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsd': 'http://www.w3.org/2001/XMLSchema'}

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and escape text for XML."""
        if not text:
            return None

        # Remove HTML tags and decode HTML entities
        cleaned = html.unescape(text)
        # Remove common HTML tags that might still be present
        import re

        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip() if cleaned.strip() else None

    def _join_list(self, items: list, separator: str = ', ') -> Optional[str]:
        """Join a list of items into a string."""
        if not items:
            return None
        return separator.join(str(item) for item in items if item)

    def _determine_age_rating(self, manga: MangaDetails) -> str:
        """Determine age rating based on manga metadata."""
        if manga.is_adult:
            return "Adults Only 18+"

        # Check tags for age-appropriate content indicators
        if manga.tags:
            adult_tags = [tag.name.lower() for tag in manga.tags if tag.is_adult]
            if adult_tags:
                return "Mature 17+"

            # Look for specific content indicators
            tag_names = [tag.name.lower() for tag in manga.tags]
            if any(tag in tag_names for tag in ['ecchi', 'violence', 'gore']):
                return "Teen"
            elif any(tag in tag_names for tag in ['school', 'slice of life', 'comedy']):
                return "Everyone 10+"

        return "Unknown"

    def _determine_language_iso(self, manga: MangaDetails) -> str:
        """Determine language ISO code based on country of origin."""
        country_to_lang = {
            'JP': 'ja',  # Japanese
            'KR': 'ko',  # Korean
            'CN': 'zh',  # Chinese
            'TW': 'zh-TW',  # Traditional Chinese
        }
        country = manga.country_of_origin or 'JP'
        return country_to_lang.get(country, 'ja')  # Default to Japanese

    def create_comic_info_data(
        self,
        manga: MangaDetails,
        volume: Optional[int] = None,
        chapter: Optional[str] = None,
        scan_info: Optional[str] = None,
    ) -> ComicInfoData:
        """Create ComicInfoData from manga details."""

        # Determine title
        title = manga.get_primary_title()
        if volume:
            title = f"{title} Volume {volume}"
        elif chapter:
            title = f"{title} Chapter {chapter}"

        # Get creators
        authors = manga.get_authors()
        artists = manga.get_artists()
        publishers = manga.get_publishers()
        main_characters = manga.get_main_characters()

        # Process description
        summary = self._clean_text(manga.description)

        # Get date information
        year = month = day = None
        if manga.start_date:
            year = manga.start_date.year
            month = manga.start_date.month
            day = manga.start_date.day

        # Determine format
        format_type = "Digital"  # Default for downloaded manga
        if manga.format == "ONE_SHOT":
            format_type = "One-Shot"

        return ComicInfoData(
            title=title,
            series=manga.get_primary_title(),
            number=str(volume) if volume else str(chapter) if chapter else None,
            count=manga.volumes,
            volume=volume,
            summary=summary,
            notes=f"Generated from AniList ID: {manga.id}",
            year=year,
            month=month,
            day=day,
            writer=self._join_list(authors),
            penciller=self._join_list(artists),
            cover_artist=self._join_list(artists),  # Usually same as penciller for manga
            publisher=self._join_list(publishers),
            genre=self._join_list(manga.genres or []),
            tags=self._join_list([tag.name for tag in (manga.tags or []) if not tag.is_spoiler]),
            web=manga.site_url,
            language_iso=self._determine_language_iso(manga),
            format=format_type,
            black_and_white="Yes" if manga.country_of_origin == 'JP' else "Unknown",
            manga=manga.get_reading_direction(),
            characters=self._join_list(main_characters),
            main_character_or_team=main_characters[0] if main_characters else None,
            scan_information=scan_info,
            age_rating=self._determine_age_rating(manga),
            community_rating=manga.average_score / 20.0 if manga.average_score else None,  # Convert from 0-100 to 0-5
        )

    def generate_comic_info_xml(self, comic_data: ComicInfoData) -> str:
        """Generate ComicInfo.xml content from ComicInfoData."""

        # Create root element
        root = etree.Element("ComicInfo")
        root.set("{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation", "ComicInfo.xsd")

        # Mapping of ComicInfoData fields to XML elements
        field_mapping = {
            'title': 'Title',
            'series': 'Series',
            'number': 'Number',
            'count': 'Count',
            'volume': 'Volume',
            'summary': 'Summary',
            'notes': 'Notes',
            'year': 'Year',
            'month': 'Month',
            'day': 'Day',
            'writer': 'Writer',
            'penciller': 'Penciller',
            'inker': 'Inker',
            'colorist': 'Colorist',
            'letterer': 'Letterer',
            'cover_artist': 'CoverArtist',
            'editor': 'Editor',
            'translator': 'Translator',
            'publisher': 'Publisher',
            'imprint': 'Imprint',
            'genre': 'Genre',
            'tags': 'Tags',
            'web': 'Web',
            'page_count': 'PageCount',
            'language_iso': 'LanguageISO',
            'format': 'Format',
            'black_and_white': 'BlackAndWhite',
            'manga': 'Manga',
            'characters': 'Characters',
            'teams': 'Teams',
            'locations': 'Locations',
            'main_character_or_team': 'MainCharacterOrTeam',
            'scan_information': 'ScanInformation',
            'story_arc': 'StoryArc',
            'story_arc_number': 'StoryArcNumber',
            'series_group': 'SeriesGroup',
            'age_rating': 'AgeRating',
            'community_rating': 'CommunityRating',
            'review': 'Review',
            'gtin': 'GTIN',
        }

        # Add elements to root
        for field_name, xml_name in field_mapping.items():
            value = getattr(comic_data, field_name)
            if value is not None:
                element = etree.SubElement(root, xml_name)
                element.text = str(value)

        # Generate XML string
        xml_str = etree.tostring(root, encoding='unicode', pretty_print=True)

        # Add XML declaration manually
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str = xml_declaration + xml_str

        return xml_str

    def generate_comic_info(
        self,
        manga: MangaDetails,
        volume: Optional[int] = None,
        chapter: Optional[str] = None,
        scan_info: Optional[str] = None,
    ) -> str:
        """Generate ComicInfo.xml content from manga details."""
        comic_data = self.create_comic_info_data(manga, volume, chapter, scan_info)
        return self.generate_comic_info_xml(comic_data)
