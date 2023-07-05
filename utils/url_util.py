import requests
from bs4 import BeautifulSoup


def get_webpage_content(url):
    url = url.strip()
    r = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        },
    )
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text().strip()
    text = text.replace("\n\n", "\n").replace("\r\r", "\r").replace("\r\n\r\n", "\r\n")
    return text
