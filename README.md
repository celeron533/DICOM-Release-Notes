# DICOM Release Notes

This project collects DICOM release-note data and presents a consolidated summary of the Correction Proposals (CPs) and Supplements incorporated into DICOM releases. It helps readers see which DICOM parts changed in each release, find related documents, and download the summary in common data formats.

The source release notes and document listings are published by [DICOM](https://dicom.nema.org/medical/dicom/). This repository downloads and processes that source material; it is not an official DICOM publication.

## How to use

Open the [deployed GitHub Pages site](https://celeron533.github.io/DICOM-Release-Notes/) to:

- Browse the CP and Supplement summary across releases since 2014.
- Select a DICOM version to view links to the corresponding DICOM parts.
- Download the displayed data as CSV, JSON, XLSX, or HTML.

The generated JSON is also available as `data/consolidated.json` (summary data) and `data/consolidated_info.json` (generation time and included versions) in the published site.

## Development

The Python dependencies and supported Python version are declared in `pyproject.toml`; `poetry.lock` records the resolved dependency versions. The main runtime dependencies are Requests, lxml, and pandas.

### Data processing flow

The pipeline entry point is `src/dicom-release-notes/start.py`. It runs these stages in order:

1. **Download release-note XML** (`download_release_notes.py`): reads the DICOM release directory, downloads release-note XML files for releases from 2014 onward, and checks the current release-note directory for the latest file. XML files are saved as `downloaded/releasenotes_<version>.xml`. If a version's file already exists, its download is skipped. The downloader tries the release-specific location first and falls back to the `current` directory if needed.
2. **Download the final document listing** (`download_document_list.py`): fetches the DICOM `final` listing and saves it as `downloaded/final.html`.
3. **Extract the document listing** (`extract_document_list.py`): parses `final.html`, selects Correction Proposal (`cp`) and Supplement (`sup`) entries, groups the listed files by document ID, and writes `data/extracted/document_list.json`.
4. **Extract release-note content** (`extract_release_notes.py`): parses the downloaded DocBook XML files and extracts the “Changes to Parts,” “Supplements Incorporated,” and “Correction Items Incorporated” sections. The intermediate results are written to `data/extracted/change_of_parts.json`, `data/extracted/supplements_incorporated.json`, and `data/extracted/correction_items_incorporated.json`.
5. **Consolidate and enrich the data** (`post_process.py`): groups changed parts by release and document ID, adds document names and descriptions where available, associates related document filenames, and writes `data/consolidated.json`. It also writes `data/consolidated_info.json` with the generation timestamp and included versions.

In short:

```text
DICOM release directory ──> release-note XML ──> extracted release changes ─┐
DICOM final listing ──────> document-list HTML ──> extracted document data ─┴─> consolidated JSON
```

### Run the data pipeline manually

You need Python 3.14 or newer, [Poetry](https://python-poetry.org/), and an internet connection to the DICOM source site.

From the repository root:

```powershell
poetry install --no-root
poetry run python src/dicom-release-notes/start.py
```

The script logs progress to the console and `app.log`. Raw downloads are stored in `downloaded/`; extracted intermediates and consolidated output are stored in `data/`.

**Before running the pipeline again**, remove the existing extracted intermediate data. Release-note extraction appends to its JSON files, so leaving them in place can duplicate records. The downloader also skips XML files that already exist; remove any cached `downloaded/releasenotes_<version>.xml` files that you want it to fetch again.

For a **clean** extraction on PowerShell:

```powershell
if (Test-Path data\extracted) { Remove-Item -Recurse -Force data\extracted }
poetry run python src/dicom-release-notes/start.py
```

### Automation and deployment

The GitHub Actions workflow in `.github/workflows/build.yml` runs the pipeline on pushes to `main`, on a schedule, and when manually dispatched. It publishes `index.html` and the two consolidated JSON files to GitHub Pages. A manually dispatched run can be configured not to deploy.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
