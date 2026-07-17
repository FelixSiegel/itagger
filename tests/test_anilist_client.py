import vcr

from itagger.anilist_client import AniListClient


def filter_bad_responses(response):
    if response['status']['code'] >= 400:
        return None  # Tells VCR to discard this response
    return response


my_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['uri', 'method', 'body'],
    before_record_response=filter_bad_responses,
)


@my_vcr.use_cassette('search_bonnouji.yaml')
def test_search_manga():
    client = AniListClient()
    results = client.search_manga("Bonnouji")

    assert len(results) > 0
    # Bonnouji's romaji title is Bonnouji
    assert any(r.title_romaji == 'Bonnouji' for r in results)


@my_vcr.use_cassette('get_bonnouji_details.yaml')
def test_get_manga_details():
    client = AniListClient()
    # Bonnouji's AniList ID is 58226
    manga = client.get_manga_details(58226)

    assert manga is not None
    assert manga.id == 58226
    assert manga.title_romaji == 'Bonnouji'

    authors = manga.get_authors()
    assert len(authors) > 0
    assert 'Aki Eda' in authors

    assert manga.format == 'MANGA'
    assert manga.country_of_origin == 'JP'
