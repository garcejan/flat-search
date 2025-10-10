import pandas as pd
import tqdm
import os
from dotenv import load_dotenv
from scraper_utils import get_detail_url_page

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
SREALITY_MAIN_URL = os.getenv("SREALITY_MAIN_URL")

########################
# Main page parsing
########################


def parse_size(size_str):
    size_list = (
        size_str.replace("Prodej bytu", "")
        .replace("m²", "")
        .strip()
        .split(" ", maxsplit=1)
    )
    return size_list[0], size_list[1] + " m²"


def convert_to_price_per_sqm(row):
    try:
        return round(
            (
                int(row["Cena"].replace("Kč", "").replace(" ", ""))
                / int(row["Užitná plocha"].replace(" m²", ""))
                if row["Cena"] and row["Užitná plocha"]
                else None
            ),
        )
    except:
        return None


def parse_main_page(elements) -> pd.DataFrame:
    results = []
    for el in tqdm.tqdm(elements, desc="Parsing main page elements"):
        href = "https://www.sreality.cz" + el.get("href")
        if not "/detail/prodej/byt" in href or "TIP" in el.getText(strip=True):
            continue
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
    df = pd.DataFrame(results)
    df["Dispozice"], df["Užitná plocha"] = zip(*df["Info"].map(parse_size))
    df["Cena za m²"] = df.apply(convert_to_price_per_sqm, axis=1)
    return df


def get_main_page(main_url: str) -> pd.DataFrame:
    soup = get_detail_url_page(main_url)
    elements = soup.find_all(
        "a",
        class_="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1s6ohwi",
    )
    df = parse_main_page(elements)
    return df


########################
# Detail page parsing
########################


def get_energy_rating(soup):
    elements = soup.find_all("div", class_="MuiStack-root css-a5aig2")
    unique_texts = set()
    for div in elements:
        for p in div.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                unique_texts.add(text)
    return " - ".join(list(unique_texts))


def get_general_info(soup):
    elements = soup.find_all("div", class_="css-gvoll6")
    d = {}
    for e in elements:
        k, v = e.get_text(strip=True).replace("\xa0", " ").split(":")
        try:
            d[k] = pd.to_datetime(v, dayfirst=True)
        except ValueError:
            pass
    return d


def get_detail(url):
    detail_info_d = {}
    detail_info_d["URL"] = url
    soup = get_detail_url_page(url)
    detail_info_d |= get_general_info(soup)
    detail_info_d["Energetický štítek"] = get_energy_rating(soup)
    return detail_info_d


###################################
# Main function for SReality
###################################


def get_sreality_offers():
    df = get_main_page(SREALITY_MAIN_URL)
    detail_info_list = []
    for url in tqdm.tqdm(df["URL"].unique(), desc="Processing detail pages"):
        # print(f"Processing detail for: {url}")
        detail_info_list.append(get_detail(url))
    print(f"Collected detail info for {len(detail_info_list)} flats.")
    df_sreality = pd.merge(df, pd.DataFrame(detail_info_list), on="URL")
    df_sreality["Web"] = "SReality"
    return df_sreality
