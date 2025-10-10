import os
from dotenv import load_dotenv
import pandas as pd
from bezrealitky_scraper import get_bezrealitky_offers
from sreality_scraper import get_sreality_offers
from excel_utils import create_excel
from notify_utils import generate_notification

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
EXCEL_PATH = os.getenv("EXCEL_PATH")


#############################
# Get latest available data
#############################
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


def create_final_dataset(
    df_sreality: pd.DataFrame, df_bezrealitky: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge data from both websites, mark new offers, and sort by interest and price per sqm.
    """

    print("Merging data from both websites...")
    df_today = pd.concat([df_sreality, df_bezrealitky]).reset_index(drop=True)

    df_today = df_today[
        [
            "Web",
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
    print("Retrieving data from yesterday...")
    df_prev = get_previous_data(excel_path=EXCEL_PATH)
    df_today["Novinka"] = df_today["URL"].apply(
        lambda x: "NOVINKA!" if not x in df_prev["URL"].unique() else ""
    )
    df_final = (
        pd.merge(df_today, df_prev, on="URL", how="left")
        .fillna("")
        .sort_values(
            by=["Zájem", "Energetický štítek", "Cena za m²"],
            ascending=[False, False, True],
        )
    )
    return df_final


#############################
#           MAIN
#############################
def main():
    print("Starting SReality scraping process...")
    df_sreality = get_sreality_offers()
    print("SReality scraping completed.")
    print("================================================================")
    print("Starting BezRealitky scraping process...")
    df_bezrealitky = get_bezrealitky_offers()
    print("BezRealitky scraping completed.")
    print("================================================================")
    df_final = create_final_dataset(df_sreality, df_bezrealitky)
    print("Final dataframe created.")
    ("================================================================")
    create_excel(df_final, excel_path=EXCEL_PATH)

    generate_notification(df_final)


if __name__ == "__main__":
    main()
