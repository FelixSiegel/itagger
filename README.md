<div align="center" style="margin-top: 20px">
  <a href="https://github.com/FelixSiegel/itagger">
        <img src="assets/logos/logo.svg" alt="Logo" width="120" height="120" />
    </a>
    <h1 style="margin-top: 0">iTagger</h1>
</div>

[![Language: Python](https://img.shields.io/badge/Language-Python-green)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A Python tool for creating `ComicInfo.xml` files for manga using the AniList API. This tool follows the ComicInfo schema specifications from [The Anansi Project](https://anansi-project.github.io/docs/comicinfo/documentation).

## Features

- 🔍 **Search manga** by title using AniList's comprehensive database
- 📊 **Fetch detailed metadata** including authors, artists, genres, tags, and more
- 📄 **Generate ComicInfo.xml** files compliant with the ComicInfo v2.1 schema
- 🎯 **Volume/chapter-specific** metadata generation
- 🌐 **Multi-language support** with proper language ISO codes
- 📚 **Batch processing** for multiple volumes
- 🎨 **Rich metadata** including character information, reading direction, age ratings

## Installation

### Using uv (Recommended)

Install the tool using [uv](https://docs.astral.sh/uv/):

```bash
uv tool install itagger
```

### Using pip

Install from PyPI using pip:

```bash
pip install itagger
```

Or install in development mode from source:

```bash
git clone https://github.com/FelixSiegel/itagger
cd itagger
pip install -e .
```

### Manual Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install requests lxml click python-dateutil
```

or using uv, just run:

```bash
uv sync
```

## Usage

### Command Line Interface

The tool provides a CLI with several commands:

```text
  batch     Generate ComicInfo.xml files for multiple volumes of a manga...
  embed     Embed ComicInfo.xml metadata directly into CBZ files.
  generate  Generate ComicInfo.xml for a specific manga.
  search    Search for manga on AniList.
```

You can get help for each command using the `--help` flag.

#### Search for manga

Syntax:

```sh
itagger search [OPTIONS] QUERY
```

Example:

```bash
itagger search --limit 5 "Attack on Titan"
```

The command returns a list of matching manga titles along with their AniList IDs and other basic information.

#### Generate ComicInfo.xml for a specific manga (requires AniList ID)

Syntax:

```sh
itagger generate [OPTIONS] MANGA_ID
```

Example:

```bash
itagger generate --volume 1 --scan-info "My Scanlation Group" 105778
```

This command generates a `ComicInfo.xml` file for volume 1 of the manga with AniList ID `105778` (Chainsaw Man) and includes the specified [scanlation group](https://anansi-project.github.io/docs/comicinfo/documentation#scaninformation) in the metadata.

You can find the AniList ID using the `search` command or by visiting the manga's page on AniList (the ID is in the URL).

#### Batch generate for multiple volumes

Syntax:

```sh
itagger batch [OPTIONS] QUERY
```

Example:

```bash
itagger batch --volumes "1-10" --output-dir "output/" "One Piece"
```

This command searches for "One Piece" on AniList, retrieves its AniList ID, and generates `ComicInfo.xml` files for volumes 1 to 10, saving them in the specified output directory.

#### Embed metadata directly into CBZ files

Syntax:

```sh
itagger embed [OPTIONS] CBZ_DIR MANGA_ID
```

Examples:

```bash
# Embed metadata (from Manga by ID) into existing CBZ files for Komga/Kavita
itagger embed /path/to/cbz/folder 30933

# For specific range of volumes/chapters
itagger embed --range "1-10" /path/to/cbz/folder 30933

# For volume-based CBZ files
itagger embed --metadata-type volumes --pattern "v{:02d}.cbz" /path/to/cbz/folder 30933

# Dry run to see what would be processed
itagger embed --dry-run /path/to/cbz/folder 30933
```

Also read the [KOMGA_KAVITA_GUIDE.md](KOMGA_KAVITA_GUIDE.md) for more details on embedding metadata into CBZ files.

### Programmatic Usage

```python
from itagger.anilist_client import AniListClient
from itagger.comicinfo_generator import ComicInfoGenerator

# Initialize clients
client = AniListClient()
generator = ComicInfoGenerator()

# Search for manga
results = client.search_manga("Naruto", limit=5)
print(f"Found {len(results)} results")

# Get detailed information
manga = client.get_manga_details(results[0].id)

# Generate ComicInfo.xml
comic_info = generator.generate_comic_info(
    manga=manga,
    volume=1,
    scan_info="Example Scanlation Group"
)

# Save to file
with open("ComicInfo.xml", "w", encoding="utf-8") as f:
    f.write(comic_info)
```

## ComicInfo.xml Fields

The tool maps AniList data to ComicInfo.xml fields according to the schema:

| ComicInfo Field | Source | Description |
|----------------|--------|-------------|
| `Title` | Manga title + volume/chapter | Full title including volume/chapter info |
| `Series` | Primary title | Series name (English preferred, fallback to Romaji) |
| `Number` | Volume/Chapter | Volume or chapter number |
| `Count` | Volume count | Total volumes in series |
| `Volume` | Volume number | Specific volume number |
| `Summary` | Description | Cleaned description without HTML |
| `Year/Month/Day` | Start date | Publication start date |
| `Writer` | Staff with "Story" role | Authors/writers |
| `Penciller` | Staff with "Art" role | Artists |
| `Publisher` | Studios | Publishing studios |
| `Genre` | Genres | Comma-separated genres |
| `Tags` | Tags (non-spoiler) | Comma-separated tags |
| `Web` | Site URL | AniList page URL |
| `LanguageISO` | Country of origin | Language code (ja, ko, zh, etc.) |
| `Manga` | Country + format | Reading direction (YesAndRightToLeft for JP) |
| `Characters` | Main characters | Main character names |
| `AgeRating` | Tags + adult flag | Age appropriateness rating |
| `CommunityRating` | Average score | Rating converted to 0-5 scale |

### Example Output

```xml
<?xml version='1.0' encoding='UTF-8'?>
<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ComicInfo.xsd">
  <Title>Attack on Titan Volume 1</Title>
  <Series>Attack on Titan</Series>
  <Number>1</Number>
  <Count>34</Count>
  <Volume>1</Volume>
  <Summary>Hundreds of years ago, horrifying creatures which resembled humans appeared...</Summary>
  <Notes>Generated from AniList ID: 53390</Notes>
  <Year>2009</Year>
  <Month>9</Month>
  <Day>9</Day>
  <Writer>Hajime Isayama</Writer>
  <Penciller>Hajime Isayama</Penciller>
  <CoverArtist>Hajime Isayama</CoverArtist>
  <Publisher>Kodansha</Publisher>
  <Genre>Action, Drama, Fantasy, Horror</Genre>
  <Tags>Survival, Military, Tragedy, Gore, War</Tags>
  <Web>https://anilist.co/manga/53390</Web>
  <LanguageISO>ja</LanguageISO>
  <Format>Digital</Format>
  <BlackAndWhite>Yes</BlackAndWhite>
  <Manga>YesAndRightToLeft</Manga>
  <Characters>Eren Yeager, Mikasa Ackerman, Armin Arlert</Characters>
  <MainCharacterOrTeam>Eren Yeager</MainCharacterOrTeam>
  <AgeRating>Mature 17+</AgeRating>
  <CommunityRating>4.3</CommunityRating>
</ComicInfo>
```

## AniList API Integration

The tool uses AniList's GraphQL API to fetch comprehensive manga metadata:

- **Search**: Finds manga by title with popularity and score sorting
- **Details**: Retrieves full metadata including staff, characters, tags, and more
- **No authentication required**: Uses public API endpoints
- **Rate limiting**: Respectful API usage with proper error handling

## Schema Compliance

Generated ComicInfo.xml files follow the [ComicInfo v2.1 schema](https://anansi-project.github.io/docs/comicinfo/schemas/v2.1) specifications:

- Proper XML structure and encoding
- Correct data types for numeric fields
- Enumerated values for specific fields (Manga, AgeRating, etc.)
- Optional field handling
- HTML entity escaping

## Dependencies

- `requests`: HTTP client for AniList API
- `lxml`: XML processing and generation
- `click`: Command-line interface framework
- `python-dateutil`: Date parsing utilities

## License

This project is open source and available under the [GNU General Public License v3.0](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Acknowledgments

- [AniList](https://anilist.co/) for providing the comprehensive manga database API
- [The Anansi Project](https://anansi-project.github.io/) for ComicInfo schema documentation
- [uv](https://docs.astral.sh/uv/) for making the whole build and installation process easier
- The manga and digital comics community for standardization efforts
