#Membuat script scraper untuk mencari lokasi liburan
#Menggunakan selenium
from selenium import webdriver
from seleq.webdriver.chrome.service import service
from bs4 import BeautifulSoup
import pandas as pd 
import time

opsi = webdriver.ChromeOption()
opsi.add_argumen('--headless')
servis = service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, option=opsi)
print(driver.title)

url = "https://www.traveloka.com/en-id"

response = requests.get(url)
soup = BeautifulSoup(response.text "html.parser")

nama = item.find("tag", class_="judul").get_text()

data.append({
    "Nama": nama,
})

#Simpan ke excel
import pandas as pddf = pd.Dataframe(data)
df.to_excel("output.xlsx", index=False)