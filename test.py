import requests
from bs4 import BeautifulSoup


url = "https://cashback.opera.com/br/shops/centauro"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


response = requests.get(url, headers=headers, timeout=10)
print(response.status_code)