from itagger.comicinfo_generator import ComicInfoGenerator
from itagger.models import MangaDetails, StaffMember


def test_comicinfo_generator():
    manga = MangaDetails(
        id=123,
        title_romaji='Test Manga',
        title_english='Test Manga English',
        staff=[StaffMember(id=1, name='Author Name', role='Story')],
        country_of_origin='JP',
        is_adult=False,
    )
    generator = ComicInfoGenerator()
    xml_str = generator.generate_comic_info(manga, volume=1)

    assert '<Title>Test Manga English Volume 1</Title>' in xml_str
    assert '<Writer>Author Name</Writer>' in xml_str
    assert '<Manga>YesAndRightToLeft</Manga>' in xml_str
    assert '<LanguageISO>ja</LanguageISO>' in xml_str


def test_clean_text():
    generator = ComicInfoGenerator()
    assert generator._clean_text('<b>Hello</b> <br>World') == 'Hello World'
