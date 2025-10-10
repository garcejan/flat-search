import re
import pandas as pd
import tqdm
import os
from dotenv import load_dotenv
from scraper_utils import get_detail_url_page


load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BEZREALITKY_MAIN_URL = os.getenv("BEZREALITKY_MAIN_URL")

########################
# Main page parsing
########################


def parse_main_page(elements) -> pd.DataFrame:
    """
    For a list of BeautifulSoup element nodes (e.g., property cards),
    extract:
        - Info, location, href from h2 with class 'PropertyCard_propertyCardHeadline___diKI'
        - layout and size from features list with class 'FeaturesList_featuresList__75Wet featuresList mt-3'
        - price and price per metre from div with class 'PropertyPrice_propertyPrice__lthza propertyPrice mb-0 mt-3'
        - additional text from div with class 'PropertyCard_propertyCardImageHolder__Dxypp'

    Returns a list of dicts named `results`.
    """
    results = []
    for el in elements:

        # Extract info, location, href from h2
        info = None
        location = None
        href = None
        h2 = el.find(class_="PropertyCard_propertyCardHeadline___diKI")
        if h2:
            info = h2.get_text(separator=" | ", strip=True)
            location = info.split(" | ")[-1] if " | " in info else ""
            a = h2.find("a")
            if a:
                href = a.get("href")

        # Extract layout and size from features list
        features = el.find(class_="FeaturesList_featuresList__75Wet featuresList mt-3")
        if features:
            features_text = features.get_text(separator="|", strip=True)
        layout = features_text.split("|")[0] if "|" in features_text else ""
        size_m2 = (
            features_text.split("|")[-1].replace("\xa0", " ")
            if "|" in features_text
            else ""
        )

        # Extract price and price per metre from features list
        prices = el.find(
            class_="PropertyPrice_propertyPrice__lthza propertyPrice mb-0 mt-3"
        )
        if prices:
            prices_text = (
                prices.get_text(
                    separator="|",
                    strip=True,
                )
                .replace("\xa0", " ")
                .replace("|(", "")
                .replace("|)", "")
            )
        price = prices_text.split("|")[0] if "|" in prices_text else ""
        price_per_metre = (
            int(prices_text.split("|")[-1].replace(" ", "").replace("Kč/m²", ""))
            if "|" in prices_text
            else ""
        )

        results.append(
            {
                "Info": info,
                "Lokalita": location,
                "Cena": price,
                "URL": href,
                "Dispozice": layout,
                "Užitná plocha": size_m2,
                "Cena za m²": price_per_metre,
            }
        )
    df = pd.DataFrame(results)
    return df


def get_main_page(main_url: str) -> pd.DataFrame:
    soup = get_detail_url_page(main_url)
    elements = soup.find_all(
        "article",
        class_="PropertyCard_propertyCard__moO_5 propertyCard PropertyCard_propertyCard--landscape__XvPmC PropertyCard_propertyCard--disable-link-mask__iJQGG",
    )
    df = parse_main_page(elements)
    return df


########################
# Detail page parsing
########################


def get_general_info(soup):
    energy_rating = ""

    for tbody in soup.find_all("tbody"):
        trs = tbody.find_all("tr")
        for tr in trs:
            row_text = tr.get_text(strip=True, separator="|")

            # PARSE ONLY ENERGY RATING NOW
            if "PENB" in row_text:
                energy_rating = row_text.split("|")[-1]

    return {"Energetický štítek": energy_rating}


def get_detail(url):
    detail_info_d = {}
    detail_info_d["URL"] = url
    soup = get_detail_url_page(url)
    detail_info_d |= get_general_info(soup)

    return detail_info_d


###################################
# Main function for SReality
###################################


def get_bezrealitky_offers() -> pd.DataFrame:
    df = get_main_page(BEZREALITKY_MAIN_URL)

    detail_info_list = []
    for url in tqdm.tqdm(df["URL"].unique(), desc="Processing detail pages"):
        details = get_detail(url)

        unapproved_energy_ratings = re.compile("D|E|F|G|H")
        if not unapproved_energy_ratings.search(details["Energetický štítek"]):
            detail_info_list.append(details)

    print(f"Collected detail info for {len(detail_info_list)} flats.")
    df_bezrealitky = pd.merge(df, pd.DataFrame(detail_info_list), on="URL", how="right")
    df_bezrealitky["Web"] = "BezRealitky"
    return df_bezrealitky
