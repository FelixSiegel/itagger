# Komga/Kavita Metadata Setup Guide

## What You Need to Do

For **Komga** or **Kavita** to recognize metadata in your CBZ files, the `ComicInfo.xml` file must be **inside** each CBZ archive, not outside it.

## Your Current Structure

```plaintext
Elfen-Lied/
├── c001.cbz
├── c002.cbz
├── c003.cbz
├── c004.cbz
├── c005.cbz
├── c006.cbz
├── c007.5.cbz
├── c007.cbz
├── c008.cbz
└── c009.cbz
```

## Steps to Add Metadata

### 1. Use the integrated embed command

The manga metadata tool now includes a built-in command to embed ComicInfo.xml directly into CBZ files.

### 2. Add ComicInfo.xml to each CBZ file

**Option A: Use the integrated embed command (Recommended):**

```bash
# For Elfen Lied chapters 1-9
python main.py embed /path/to/Elfen-Lied 30933 --range "1-9"

# With custom scan information
python main.py embed /path/to/Elfen-Lied 30933 --range "1-9" --scan-info "Your Scanlation Group"

# Dry run to see what would be processed
python main.py embed /path/to/Elfen-Lied 30933 --range "1-9" --dry-run
```

**Option B: Manual process**
For each CBZ file:

1. Extract the CBZ (it's just a ZIP file)
2. Add the corresponding ComicInfo.xml to the root
3. Re-compress as CBZ

### 3. Expected Result

After processing, each CBZ file will contain:

```plaintext
c001.cbz
├── ComicInfo.xml          ← This is what Komga/Kavita reads
├── 001.jpg
├── 002.jpg
└── ...other image files
```

## ComicInfo.xml Content Example

Each chapter will have metadata like:

```xml
<ComicInfo>
  <Title>Elfen Lied Chapter 1</Title>
  <Series>Elfen Lied</Series>
  <Number>1</Number>
  <Count>12</Count>
  <Writer>Lynn Okamoto</Writer>
  <Genre>Action, Drama, Horror, Psychological, Romance, Supernatural</Genre>
  <Manga>YesAndRightToLeft</Manga>
  <!-- ... more metadata ... -->
</ComicInfo>
```

## What Komga/Kavita Will Show

With the ComicInfo.xml properly embedded, you'll see:

- ✅ **Series Name**: "Elfen Lied"
- ✅ **Chapter Numbers**: 1, 2, 3, 4, 5, 6, 7, 7.5, 8, 9
- ✅ **Author**: Lynn Okamoto
- ✅ **Genres**: Action, Drama, Horror, Psychological, Romance, Supernatural
- ✅ **Reading Direction**: Right-to-left (manga)
- ✅ **Publication Date**: 2002-06-06
- ✅ **Total Volumes**: 12
- ✅ **Age Rating**: Teen

## File Naming for Better Recognition

Your current naming (`c001.cbz`, `c002.cbz`, etc.) works well. For optimal recognition:

- ✅ **Good**: `c001.cbz`, `c002.cbz`, `c007.5.cbz`
- ✅ **Also Good**: `Elfen Lied - 001.cbz`, `Elfen Lied - Chapter 001.cbz`
- ❌ **Avoid**: Random names like `file1.cbz`, `download.cbz`

## Troubleshooting

### If metadata isn't showing

1. **Check CBZ contents**: Ensure `ComicInfo.xml` is at the root level inside the CBZ
2. **Refresh library**: Force a library scan in Komga/Kavita
3. **Check logs**: Look for XML parsing errors in Komga/Kavita logs
4. **Validate XML**: Ensure ComicInfo.xml is valid XML (our tool generates valid files)

### Common issues

- ❌ ComicInfo.xml placed next to CBZ files (should be inside)
- ❌ ComicInfo.xml in a subfolder inside CBZ (should be at root)
- ❌ Incorrect XML format (our tool prevents this)
- ❌ Case sensitivity: must be exactly `ComicInfo.xml`

## Alternative: Volume-Based Structure

If you prefer volume-based organization:

```plaintext
Elfen-Lied/
├── Elfen Lied v01.cbz
├── Elfen Lied v02.cbz
└── ...
```

Generate volume metadata instead:

```bash
python main.py embed /path/to/Elfen-Lied 30933 --metadata-type volumes --pattern "Elfen Lied v{:02d}.cbz" --range "1-12"
```

## Next Steps

1. Run the embed command: `python main.py embed /path/to/Elfen-Lied 30933 --range "1-9"`
2. Refresh your Komga/Kavita library
3. Enjoy properly organized manga with rich metadata!
