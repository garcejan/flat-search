from bs4 import BeautifulSoup
import requests


def get_detail_url_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
