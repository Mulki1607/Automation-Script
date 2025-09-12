import requests
from bs4 import BeautifulSoup
import pandas as pd

#1. Tentukan website yang ingin di scrape
url = "https://quotes.toscrape.com/"

#2. Ambil konten dari website
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

#3. Cari semua elemen qoute
quotes = soup.find_all("span", class_="text")
authors = soup.find_all("small", class_="author")

#4. Simpan kelist python
data = []
for i in range(len(quotes)):
    data.append({
        "Quote": quotes[i].text,
        "Author": authors[i].text
    })

#5. Buat DataFrame dengan pandas
df=pd.DataFrame(data)

#. Simpan Ke Excel
df.to_excel("quote.xlsx", index=False)

print("Data berhasil di simpan ke 'quoute.xlsx'")