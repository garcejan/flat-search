
<p align="center">
   <img src="https://d11-a.sdn.cz/d_11/c_img_G_J/ynXEtZ.jpeg" alt="Sreality.cz" width="180"/>
</p>
# Flat Search

This repository collects and processes apartment listings (Prague) and exports results to Excel and other artifacts. It contains both a scripted workflow (`src/main.py`) and a Jupyter notebook for exploration and iterative runs.

## What this project contains

Top-level layout (important files and folders):

- `pyproject.toml` — project metadata / build config (if using tools that read it)
- `requirements.txt` — pinned Python dependencies used by the scripts/notebook
- `notebooks/flat-search-notebook.ipynb` — exploratory notebook with the step-by-step workflow
- `scripts/run_script.sh` — convenience shell wrapper to run the main script
- `src/` — Python source files
  - `main.py` — orchestrates scraping, processing, and export
  - `sreality_scraper.py` — scraper logic for sreality.cz
  - `bezrealitky_scraper.py` — scraper logic for bezrealitky (if used)
  - `scraper_utils.py` — shared scraping helpers (requests, parsing helpers)
  - `excel_utils.py` — functions to write and format Excel reports
  - `notify_utils.py` — optional notifications (email, desktop, etc.)
- `reports/` — output files (e.g. Excel results)
- `logs/` — runtime logs

## Quickstart

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure (optional):

- Create a `.env` file at the repository root to override runtime settings (example keys used by the project):

```env
MAIN_URL=https://www.sreality.cz/hledani/your-search-url
EXCEL_PATH=reports/flat_search_results.xlsx
LOG_LEVEL=INFO
```

4. Run the scripted workflow:

```bash
# run directly with Python
python src/main.py

# or use the helper script
./scripts/run_script.sh
```

5. Or open the notebook at `notebooks/flat-search-notebook.ipynb` and run cells interactively.

## Outputs

- Excel report(s) are written to `reports/` by default (file name may be configured via `.env` or script args).
- Logs are written to the `logs/` directory.

## Short module guide

- `src/main.py` — entry point; wires scrapers, processors and exporters together. It can be run unattended.
- `src/sreality_scraper.py` — contains the site-specific scraping/parsing logic for sreality.cz listings.
- `src/bezrealitky_scraper.py` — alternative source scraper implementation.
- `src/scraper_utils.py` — common utilities for HTTP requests, retries, rate-limiting, and HTML parsing helpers.
- `src/excel_utils.py` — builds formatted Excel files, adds columns such as interest/filters, and creates separate sheets.
- `src/notify_utils.py` — helper for sending notifications (optional/experimental).

If you change public behavior in any of these modules, consider adding a small test or a notebook cell demonstrating the change.

## Development notes & etiquette

- Run responsibly: respect robots.txt and the target website's terms of service. Add delays and rate limits when scraping.
- Keep secrets (API keys, credentials) out of the repo. Put them in environment variables or an ignored `.env` file.

## License

MIT License

---

If you'd like, I can also:

- add a sample `.env.example` in the repo,
- add a short `Makefile` or `tox`/`nox` tasks for common workflows,
- or create a small test that verifies the main export function writes a valid Excel file.

Created by Jan Garcek