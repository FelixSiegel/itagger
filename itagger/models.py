"""Data models for manga metadata."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import date


@dataclass
class FuzzyDate:
    """Represents a date that may have missing components."""

    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None

    def to_date(self) -> Optional[date]:
        """Convert to a Python date object if all components are available."""
        if self.year and self.month and self.day:
            return date(self.year, self.month, self.day)
        return None

    def __str__(self) -> str:
        """String representation of the date."""
        if self.year and self.month and self.day:
            return f"{self.year}-{self.month:02d}-{self.day:02d}"
        elif self.year and self.month:
            return f"{self.year}-{self.month:02d}"
        elif self.year:
            return str(self.year)
        return "Unknown"


@dataclass
class StaffMember:
    """Represents a staff member (author, artist, etc.)."""

    id: int
    name: str
    role: str
    native_name: Optional[str] = None


@dataclass
class Character:
    """Represents a character in the manga."""

    id: int
    name: str
    native_name: Optional[str] = None
    role: str = "MAIN"  # MAIN, SUPPORTING, BACKGROUND


@dataclass
class Studio:
    """Represents a studio/publisher."""

    id: int
    name: str
    is_animation_studio: bool = False


@dataclass
class Genre:
    """Represents a genre."""

    name: str


@dataclass
class Tag:
    """Represents a tag with additional metadata."""

    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    rank: Optional[int] = None
    is_spoiler: bool = False
    is_adult: bool = False


@dataclass
class MangaSearchResult:
    """Basic manga information from search results."""

    id: int
    title_romaji: str
    title_english: Optional[str] = None
    title_native: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[FuzzyDate] = None
    end_date: Optional[FuzzyDate] = None
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None


@dataclass
class MangaDetails:
    """Detailed manga information."""

    id: int
    title_romaji: str
    title_english: Optional[str] = None
    title_native: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # FINISHED, RELEASING, NOT_YET_RELEASED, CANCELLED, HIATUS
    start_date: Optional[FuzzyDate] = None
    end_date: Optional[FuzzyDate] = None
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[Tag]] = None
    staff: Optional[List[StaffMember]] = None
    characters: Optional[List[Character]] = None
    studios: Optional[List[Studio]] = None
    country_of_origin: Optional[str] = None  # JP, KR, CN, etc.
    source: Optional[str] = None  # ORIGINAL, MANGA, LIGHT_NOVEL, etc.
    format: Optional[str] = None  # MANGA, NOVEL, ONE_SHOT, etc.
    is_adult: bool = False
    average_score: Optional[int] = None
    mean_score: Optional[int] = None
    popularity: Optional[int] = None
    favourites: Optional[int] = None
    hashtag: Optional[str] = None
    site_url: Optional[str] = None

    def __post_init__(self):
        """Initialize empty lists if None."""
        if self.genres is None:
            self.genres = []
        if self.tags is None:
            self.tags = []
        if self.staff is None:
            self.staff = []
        if self.characters is None:
            self.characters = []
        if self.studios is None:
            self.studios = []

    def get_primary_title(self) -> str:
        """Get the primary title (prefer English, fallback to Romaji)."""
        return self.title_english or self.title_romaji

    def get_authors(self) -> List[str]:
        """Get list of authors (Story role)."""
        if not self.staff:
            return []
        return [staff.name for staff in self.staff if staff.role in ['Story', 'Story & Art']]

    def get_artists(self) -> List[str]:
        """Get list of artists (Art role)."""
        if not self.staff:
            return []
        return [staff.name for staff in self.staff if staff.role in ['Art', 'Story & Art']]

    def get_main_characters(self) -> List[str]:
        """Get list of main character names."""
        if not self.characters:
            return []
        return [char.name for char in self.characters if char.role == 'MAIN']

    def get_publishers(self) -> List[str]:
        """Get list of publisher/studio names."""
        if not self.studios:
            return []
        return [studio.name for studio in self.studios]

    def is_manga_format(self) -> bool:
        """Check if this is a manga (as opposed to novel, etc.)."""
        return self.format in ['MANGA', 'ONE_SHOT'] if self.format else True

    def get_reading_direction(self) -> str:
        """Get reading direction based on country of origin."""
        if self.country_of_origin == 'JP':
            return 'YesAndRightToLeft'
        elif self.country_of_origin in ['KR', 'CN']:
            return 'Yes'  # Manhwa/Manhua typically read left-to-right
        return 'Unknown'


@dataclass
class ComicInfoData:
    """Data structure for ComicInfo.xml generation."""

    title: Optional[str] = None
    series: Optional[str] = None
    number: Optional[str] = None
    count: Optional[int] = None
    volume: Optional[int] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    writer: Optional[str] = None
    penciller: Optional[str] = None
    inker: Optional[str] = None
    colorist: Optional[str] = None
    letterer: Optional[str] = None
    cover_artist: Optional[str] = None
    editor: Optional[str] = None
    translator: Optional[str] = None
    publisher: Optional[str] = None
    imprint: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[str] = None
    web: Optional[str] = None
    page_count: Optional[int] = None
    language_iso: Optional[str] = None
    format: Optional[str] = None
    black_and_white: str = "Unknown"
    manga: str = "Unknown"
    characters: Optional[str] = None
    teams: Optional[str] = None
    locations: Optional[str] = None
    main_character_or_team: Optional[str] = None
    scan_information: Optional[str] = None
    story_arc: Optional[str] = None
    story_arc_number: Optional[str] = None
    series_group: Optional[str] = None
    age_rating: str = "Unknown"
    community_rating: Optional[float] = None
    review: Optional[str] = None
    gtin: Optional[str] = None
