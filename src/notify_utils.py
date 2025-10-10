import subprocess
import pandas as pd

# import pync


def notify(title: str, message: str):
    subprocess.run(
        ["osascript", "-e", f'display notification "{message}" with title "{title}"']
    )
    # pync.notify(
    #     message,
    #     title=title,
    #     open="/Users/gary/Documents/Personal/flat-search/reports/flat_search_results.xlsx",
    # )


def generate_notification(df: pd.DataFrame):
    print("Generating pop-up notification.")
    new_offer = any(df["Novinka"] == "NOVINKA!")
    # new_offer = True
    if new_offer:
        notify(
            "Flat search automation", "Nové inzeráty na realitkách k dispozici! 🏡🚀"
        )
    else:
        notify("Flat search automation", "Od včerejška žádný nový inzerát... 🏡🥺")
