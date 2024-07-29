# filename: ytd_gain.py

import requests
from bs4 import BeautifulSoup

# Get the 10 largest tech companies by market cap
url = "https://companiesmarketcap.com/usa/largest-companies-in-the-usa-by-market-cap/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print(soup.prettify())