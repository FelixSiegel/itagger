"""AniList API client for fetching manga metadata."""

import requests
from typing import List, Optional, Dict, Any
from .models import MangaSearchResult, MangaDetails, FuzzyDate, StaffMember, Character, Studio, Tag


class AniListClient:
    """Client for interacting with the AniList GraphQL API."""

    def __init__(self):
        self.base_url = "https://graphql.anilist.co"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

    def _make_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GraphQL request to AniList API."""
        payload = {'query': query, 'variables': variables or {}}

        response = self.session.post(self.base_url, json=payload)
        response.raise_for_status()

        data = response.json()
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data.get('data', {})

    def search_manga(self, query: str, limit: int = 10) -> List[MangaSearchResult]:
        """Search for manga by title."""
        graphql_query = """
        query ($search: String, $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(search: $search, type: MANGA, sort: [POPULARITY_DESC, SCORE_DESC]) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    status
                    startDate {
                        year
                        month
                        day
                    }
                    endDate {
                        year
                        month
                        day
                    }
                    chapters
                    volumes
                    coverImage {
                        large
                    }
                    description(asHtml: false)
                }
            }
        }
        """

        variables = {'search': query, 'page': 1, 'perPage': limit}

        data = self._make_request(graphql_query, variables)
        results = []

        for media in data.get('Page', {}).get('media', []):
            start_date = None
            if media.get('startDate'):
                start_date = FuzzyDate(
                    year=media['startDate'].get('year'),
                    month=media['startDate'].get('month'),
                    day=media['startDate'].get('day'),
                )

            end_date = None
            if media.get('endDate'):
                end_date = FuzzyDate(
                    year=media['endDate'].get('year'),
                    month=media['endDate'].get('month'),
                    day=media['endDate'].get('day'),
                )

            result = MangaSearchResult(
                id=media['id'],
                title_romaji=media['title']['romaji'],
                title_english=media['title'].get('english'),
                title_native=media['title'].get('native'),
                status=media.get('status'),
                start_date=start_date,
                end_date=end_date,
                chapters=media.get('chapters'),
                volumes=media.get('volumes'),
                cover_image=media.get('coverImage', {}).get('large'),
                description=media.get('description'),
            )
            results.append(result)

        return results

    def get_manga_details(self, manga_id: int) -> Optional[MangaDetails]:
        """Get detailed information about a specific manga."""
        graphql_query = """
        query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title {
                    romaji
                    english
                    native
                }
                description(asHtml: false)
                status
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                chapters
                volumes
                coverImage {
                    large
                }
                bannerImage
                genres
                tags {
                    name
                    description
                    category
                    rank
                    isGeneralSpoiler
                    isAdult
                }
                staff {
                    edges {
                        node {
                            id
                            name {
                                full
                                native
                            }
                        }
                        role
                    }
                }
                characters {
                    edges {
                        node {
                            id
                            name {
                                full
                                native
                            }
                        }
                        role
                    }
                }
                studios {
                    edges {
                        node {
                            id
                            name
                            isAnimationStudio
                        }
                    }
                }
                countryOfOrigin
                source
                format
                isAdult
                averageScore
                meanScore
                popularity
                favourites
                hashtag
                siteUrl
            }
        }
        """

        variables = {'id': manga_id}
        data = self._make_request(graphql_query, variables)

        media = data.get('Media')
        if not media:
            return None

        # Parse dates
        start_date = None
        if media.get('startDate'):
            start_date = FuzzyDate(
                year=media['startDate'].get('year'),
                month=media['startDate'].get('month'),
                day=media['startDate'].get('day'),
            )

        end_date = None
        if media.get('endDate'):
            end_date = FuzzyDate(
                year=media['endDate'].get('year'), month=media['endDate'].get('month'), day=media['endDate'].get('day')
            )

        # Parse tags
        tags = []
        for tag_data in media.get('tags', []):
            tag = Tag(
                name=tag_data['name'],
                description=tag_data.get('description'),
                category=tag_data.get('category'),
                rank=tag_data.get('rank'),
                is_spoiler=tag_data.get('isGeneralSpoiler', False),
                is_adult=tag_data.get('isAdult', False),
            )
            tags.append(tag)

        # Parse staff
        staff = []
        for staff_edge in media.get('staff', {}).get('edges', []):
            staff_node = staff_edge['node']
            staff_member = StaffMember(
                id=staff_node['id'],
                name=staff_node['name']['full'],
                native_name=staff_node['name'].get('native'),
                role=staff_edge.get('role', 'Unknown'),
            )
            staff.append(staff_member)

        # Parse characters
        characters = []
        for char_edge in media.get('characters', {}).get('edges', []):
            char_node = char_edge['node']
            character = Character(
                id=char_node['id'],
                name=char_node['name']['full'],
                native_name=char_node['name'].get('native'),
                role=char_edge.get('role', 'BACKGROUND'),
            )
            characters.append(character)

        # Parse studios
        studios = []
        for studio_edge in media.get('studios', {}).get('edges', []):
            studio_node = studio_edge['node']
            studio = Studio(
                id=studio_node['id'],
                name=studio_node['name'],
                is_animation_studio=studio_node.get('isAnimationStudio', False),
            )
            studios.append(studio)

        return MangaDetails(
            id=media['id'],
            title_romaji=media['title']['romaji'],
            title_english=media['title'].get('english'),
            title_native=media['title'].get('native'),
            description=media.get('description'),
            status=media.get('status'),
            start_date=start_date,
            end_date=end_date,
            chapters=media.get('chapters'),
            volumes=media.get('volumes'),
            cover_image=media.get('coverImage', {}).get('large'),
            banner_image=media.get('bannerImage'),
            genres=media.get('genres', []),
            tags=tags,
            staff=staff,
            characters=characters,
            studios=studios,
            country_of_origin=media.get('countryOfOrigin'),
            source=media.get('source'),
            format=media.get('format'),
            is_adult=media.get('isAdult', False),
            average_score=media.get('averageScore'),
            mean_score=media.get('meanScore'),
            popularity=media.get('popularity'),
            favourites=media.get('favourites'),
            hashtag=media.get('hashtag'),
            site_url=media.get('siteUrl'),
        )
