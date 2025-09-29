import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
import tqdm
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
MAIN_URL = os.getenv("MAIN_URL")
EXCEL_PATH = os.getenv("EXCEL_PATH")


########################
# Main page parsing
########################
def parse_main_page(elements):
    """Parse the main listing page elements and return a DataFrame"""
    results = []

    # Parse elements
    for el in tqdm.tqdm(elements, desc="Parsing main page elements"):
        href = "https://www.sreality.cz" + el.get("href")

        # Filer out non-apartment links and ads
        if not "/detail/prodej/byt" in href or "TIP" in el.getText(strip=True):
            continue

        # Extract size, location, price
        text_elem = el.find(class_="css-adf8sc")
        if text_elem:
            texts = [
                t.get_text(strip=True).replace("\xa0", " ")
                for t in text_elem.find_all(recursive=False)
                if not ".css" in t.get_text(strip=True)
            ]
            if not texts:
                texts = [text_elem.get_text(strip=True).replace("\xa0", " ")]
        else:
            texts = []
        size = texts[0] if len(texts) > 0 else None
        location = texts[1] if len(texts) > 1 else None
        price = texts[2] if len(texts) > 2 else None

        results.append({"Info": size, "Lokalita": location, "Cena": price, "URL": href})

    print(f"Parsed {len(results)} relevant results from main page.")

    df = pd.DataFrame(results)
    print("DataFrame head:")
    print(df.head())
    df["Dispozice"], df["Užitná plocha"] = zip(*df["Info"].map(parse_size))
    print("Parsed size columns.")
    df["Cena za m²"] = df.apply(
        lambda row: round(
            (
                int(row["Cena"].replace("Kč", "").replace(" ", ""))
                / int(row["Užitná plocha"].replace(" m²", ""))
                if row["Cena"] and row["Užitná plocha"]
                else None
            ),
        ),
        axis=1,
    )
    print("Calculated price per m².")
    return df


def get_main_page():
    """Scrape the main listing page and return a list of results"""

    print(f"Requesting main listing page: {MAIN_URL}")

    # Get main page
    response = requests.get(MAIN_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(
        "a",
        class_="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1s6ohwi",
    )
    print(f"Found {len(elements)} elements on main page.")

    # Parse main page elements
    df = parse_main_page(elements)

    return df


########################
# Detail page parsing
########################


def parse_size(size_str):
    """Parse size string into disposition and usable area"""
    # Parse the size string into disposition and usable area
    size_list = (
        size_str.replace("Prodej bytu", "")
        .replace("m²", "")
        .strip()
        .split(" ", maxsplit=1)
    )
    return size_list[0], size_list[1] + " m²"


def get_detail_url_page(url):
    """Fetch the detail page and return its soup"""
    print(f"Fetching detail page: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_energy_rating(soup):
    """Extract energy rating from the detail soup"""
    elements = soup.find_all("div", class_="MuiStack-root css-a5aig2")
    unique_texts = set()
    for div in elements:
        for p in div.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                unique_texts.add(text)
    return " - ".join(list(unique_texts))


def get_general_info(soup):
    """Extract general info (dates, etc.) from the detail soup"""
    elements = soup.find_all("div", class_="css-gvoll6")
    d = {}
    for e in elements:
        k, v = e.get_text(strip=True).replace("\xa0", " ").split(":")
        try:
            d[k] = pd.to_datetime(v, dayfirst=True)
        except ValueError:
            # Not a date, skip
            pass
    return d


def get_detail(url):
    """Get all detail info for a given flat URL"""
    detail_info_d = {}
    detail_info_d["URL"] = url
    soup = get_detail_url_page(url)
    detail_info_d |= get_general_info(soup)
    detail_info_d["Energetický štítek"] = get_energy_rating(soup)
    print(f"Detail info for {url}: {detail_info_d}")
    return detail_info_d


########################
# Get previous data
########################
def get_previous_data(excel_path=EXCEL_PATH):
    df_prev_yes = pd.read_excel(
        excel_path,
        usecols=["URL", "Zájem"],
        sheet_name="Hlavní",
    )
    df_prev_no = pd.read_excel(
        excel_path,
        usecols=["URL", "Zájem"],
        sheet_name="Vyřazené",
    )

    df_prev = pd.concat([df_prev_yes, df_prev_no]).drop_duplicates()
    return df_prev


########################
# Excel formatting
########################


def create_excel(
    df,
    excel_path=EXCEL_PATH,
):
    """
    Create an Excel file from the DataFrame with formatting and a dropdown column.

    Args:
        df (dataframe): DataFrame containing the data to export.
        excel_path (str, optional): Defaults to "flat_search_results.xlsx".
    """
    print("Filtered columns for export.")
    print(f"Saving to Excel: {excel_path}")
    # Split DataFrame into two: Hlavní (Zájem != "NE") and Vyřazené (Zájem == "NE")
    main_df = df[df["Zájem"] != "NE"].copy()
    removed_df = df[df["Zájem"] == "NE"].copy()

    # Write both DataFrames to two sheets
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        main_df.to_excel(writer, sheet_name="Hlavní", index=False)
        removed_df.to_excel(writer, sheet_name="Vyřazené", index=False)

    # Now apply formatting and data validation to both sheets
    wb = openpyxl.load_workbook(excel_path)

    for sheet_name in ["Hlavní", "Vyřazené"]:
        ws = wb[sheet_name]

        # --- CLICKABLE URLs ---
        # Make URL column clickable (as hyperlinks)
        url_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == "URL":
                url_col = idx
                break

        if url_col:
            col_letter = openpyxl.utils.get_column_letter(url_col)
            for row in range(2, ws.max_row + 1):
                cell = ws[f"{col_letter}{row}"]
                if (
                    cell.value
                    and isinstance(cell.value, str)
                    and cell.value.startswith("http")
                ):
                    cell.hyperlink = cell.value
                    cell.style = "Hyperlink"

            print(f"Processed clickable URLs in column {col_letter}.")

        # --- FORMATTING AND STYLES ---
        # Define styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F81BD")  # Blue header
        odd_fill = PatternFill("solid", fgColor="DCE6F1")  # Light blue
        even_fill = PatternFill("solid", fgColor="FFFFFF")  # White

        # Set header style
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
        print("Styled header row.")

        # Set row styles and adjust row height
        for i, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
            fill = odd_fill if i % 2 else even_fill
            for cell in row:
                cell.fill = fill
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[i].height = 30  # Adjust as needed for visibility
        print("Styled data rows.")

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            ws.column_dimensions[col_letter].width = max(15, min(max_length + 2, 50))
        print("Auto-adjusted column widths.")

        # --- DATA VALIDATION ---
        # Add data validation for 'Zájem' column if present
        interest_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == "Zájem":
                interest_col = idx
                break

        if interest_col:
            try:
                col_letter = openpyxl.utils.get_column_letter(interest_col)
                dv = DataValidation(type="list", formula1='"ANO,NE"', allow_blank=True)
                ws.add_data_validation(dv)
                dv.add(f"{col_letter}2:{col_letter}{ws.max_row}")
                print(f"Added data validation to column {col_letter}.")
            except Exception as e:
                print(f"Error adding data validation: {e}")

    wb.save(excel_path)
    print(
        f"Excel file '{excel_path}' created with two sheets ['Hlavní', 'Vyřazené'] and formatting."
    )


def main():
    # Main scraping and Excel export logic
    print("Starting main scraping process...")
    df = get_main_page()

    # Get detail info for each unique URL
    detail_info_list = []
    for url in tqdm.tqdm(df["URL"].unique(), desc="Processing detail pages"):
        print(f"Processing detail for: {url}")
        detail_info_list.append(get_detail(url))
    print(f"Collected detail info for {len(detail_info_list)} flats.")

    df_today = pd.merge(df, pd.DataFrame(detail_info_list), on="URL")
    df_today = df_today[
        [
            "Info",
            "Lokalita",
            "Cena",
            "URL",
            "Dispozice",
            "Užitná plocha",
            "Cena za m²",
            "Vloženo",
            "Upraveno",
            "Energetický štítek",
        ]
    ]
    print("Merged and sorted DataFrame.")

    # Add data from previous run
    print("Adding previous data...")
    df_prev = get_previous_data(excel_path=EXCEL_PATH)

    # Add flag for new offers
    df_today["Novinka"] = df_today["URL"].apply(
        lambda x: "NOVINKA!" if not x in df_prev["URL"].unique() else ""
    )

    # Merge today's and previous data
    df_final = (
        pd.merge(df_today, df_prev, on="URL", how="left")
        .fillna("")
        .sort_values(
            by=["Zájem", "Upraveno", "Energetický štítek", "Cena za m²"],
            ascending=[False, False, False, True],
        )
    )

    print("Final dataframe created.")

    # Export dataframe to Excel
    create_excel(
        df_final,
        excel_path=EXCEL_PATH,
    )


if __name__ == "__main__":
    main()
