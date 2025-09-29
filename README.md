
<p align="center">
   <img src="https://d11-a.sdn.cz/d_11/c_img_G_J/ynXEtZ.jpeg" alt="Sreality.cz" width="180"/>
</p>

# 🏢 Flat Search Automation

Automate the search, analysis, and review of Prague flat listings from [sreality.cz](https://www.sreality.cz) with beautiful Excel exports and smart filtering.

---

## ✨ Features

<ul>
   <li><b>Web Scraping</b>: Collects flat listings from selected Prague districts with customizable filters.</li>
   <li><b>Data Processing</b>: Extracts and cleans key information (size, location, price, energy rating, etc.).</li>
   <li><b>Excel Export</b>:
      <ul>
         <li>Outputs results to a well-formatted Excel file.</li>
         <li>Adds a <code>Zájem</code> column with dropdown options (<code>ANO</code>, <code>NE</code>) for user interest.</li>
         <li>Conditional formatting: <span style="color:green;">green</span> for <code>ANO</code>, <span style="color:red;">red</span> for <code>NE</code>.</li>
         <li>Clickable hyperlinks in the <code>URL</code> column.</li>
         <li>Two sheets:
            <ul>
               <li><b>Hlavní</b>: Flats where <code>Zájem</code> is not <code>NE</code>.</li>
               <li><b>Vyřazené</b>: Flats where <code>Zájem</code> is <code>NE</code>.</li>
            </ul>
         </li>
      </ul>
   </li>
   <li><b>.env Support</b>: Easily configure main search URL and output path via a <code>.env</code> file.</li>
</ul>

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/garcejan/flat-search.git
cd flat-search
pip install -r requirements.txt
```

### 2. Configure

Edit the <code>.env</code> file to set your search URL and output path:

```env
MAIN_URL=https://www.sreality.cz/hledani/prodej/byty/praha-2,praha-3,praha-4?...(your filters)...
EXCEL_PATH=/absolute/path/to/flat_search_results.xlsx
```

### 3. Run

<details>
<summary>Notebook</summary>

Open <code>notebooks/flat-search-notebook.ipynb</code> in Jupyter and run step by step.

</details>

<details>
<summary>Script</summary>

```bash
python src/main.py
```

</details>

### 4. Review Results

- The main output is in <code>reports/flat_search_results.xlsx</code> (or as set in <code>.env</code>).
- Open in Excel to review, filter, and mark flats of interest.

---

## 📁 File Structure

<pre>
notebooks/flat-search-notebook.ipynb   # Main Jupyter notebook for scraping and processing
src/main.py                            # Main script version of the workflow
flat_search_to_excel.py                # (Optional) Standalone script
reports/flat_search_results.xlsx       # Main Excel output with two sheets
.env                                   # Configuration for URL and output path
requirements.txt                       # Python dependencies
README.md                              # This file
</pre>

---

## ⚙️ Customization

- Adjust search filters in the <code>.env</code> file or directly in the notebook/script.
- The Excel output can be further customized for additional columns or formatting.

---

## 📝 Notes

- The script is designed for personal, non-commercial use.
- Be respectful of the target website’s terms of service and avoid excessive scraping.

---

## 📜 License

MIT License

---

<p align="center"><i>Created by Jan Garcek, 2025.09</i></p>