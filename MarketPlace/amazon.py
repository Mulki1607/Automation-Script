from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
import re
from openpyxl import load_workbook

# --- SETUP DRIVER ---
opsi = webdriver.ChromeOptions()
opsi.add_argument('--headless=new')
opsi.add_argument("--start-maximized")
opsi.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36")
opsi.add_experimental_option("excludeSwitches", ["enable-logging"])  # bersihkan log

service = Service(r"C:\Users\sn11 03.12.23\Documents\Tools\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=opsi)
driver.set_window_size(1920, 1080)

# --- LINK PENCARIAN AMAZON ---
amazon_link = "https://www.amazon.com/s?k=macbook"
driver.get(amazon_link)
time.sleep(5)

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")))

# Scroll biar lebih banyak produk muncul
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Ambil link produk
produk_links = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")

hasil = []
for i, produk in enumerate(produk_links[:10]):  # ambil 10 dulu biar ada cadangan
    try:
        url = produk.get_attribute("href")

        # Buka tab baru
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])

        # Ambil judul
        try:
            judul = wait.until(EC.presence_of_element_located((By.ID, "productTitle"))).text.strip()
        except:
            judul = "Judul tidak ditemukan"

        # --- FILTER: hanya ambil produk yang ada "MacBook" di judul ---
        if "macbook" not in judul.lower():
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(f"❌ Skip produk non-MacBook: {judul}")
            continue

        # Ambil harga
        try:
            harga = driver.find_element(By.CSS_SELECTOR, "#corePriceDisplay_desktop_feature_div span.a-offscreen").text
        except:
            try:
                harga = driver.find_element(By.CSS_SELECTOR, "span.a-price span.a-offscreen").text
            except:
                harga = "Harga tidak tersedia"

        # Ambil RAM
        try:
            ram = driver.find_element(By.CSS_SELECTOR, "div#variation_memory_size .a-button-selected span.a-button-inner").text
        except:
            match_ram = re.search(r"(\d+GB RAM)", judul)
            ram = match_ram.group(1) if match_ram else "RAM tidak disebutkan"

        # Ambil Storage
        try:
            storage = driver.find_element(By.CSS_SELECTOR, "div#variation_hard_drive_size .a-button-selected span.a-button-inner").text
        except:
            match_storage = re.search(r"(\d+TB|\d+GB SSD|\d+GB Storage)", judul)
            storage = match_storage.group(1) if match_storage else "Storage tidak disebutkan"

        # Ambil Style / Warna
        try:
            style = driver.find_element(By.CSS_SELECTOR, "div#variation_color_name .a-button-selected span.a-button-inner").text
        except:
            match_style = re.search(r"(Silver|Space Gray|Gold)", judul, re.IGNORECASE)
            style = match_style.group(1) if match_style else "Style tidak disebutkan"

        # Ambil Rating
        try:
            rating = driver.find_element(By.CSS_SELECTOR, "span[data-asin] span.a-icon-alt").text
        except:
            rating = "Rating tidak ditemukan"

        # Ambil Jumlah Review
        try:
            review = driver.find_element(By.ID, "acrCustomerReviewText").text
        except:
            review = "Review tidak ditemukan"

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"{i+1}. {judul} - {harga} | {ram} | {storage} | {style} | {rating} | {review}")
        hasil.append({
            "Judul": judul,
            "Harga": harga,
            "RAM": ram,
            "Storage": storage,
            "Style": style,
            "Rating": rating,
            "Review": review,
            "URL": url,
            "Waktu Scraping": timestamp
        })

        # Tutup tab produk & balik ke tab pencarian
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Error di produk {i+1}: {e}")

# --- SIMPAN HASIL KE EXCEL ---
df = pd.DataFrame(hasil)

# Nama file unik dengan timestamp
file_excel = f"amazon_macbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
df.to_excel(file_excel, index=False, engine="openpyxl")

# --- AUTO ADJUST COLUMN WIDTH ---
wb = load_workbook(file_excel)
ws = wb.active

for col in ws.columns:
    max_length = 0
    col_letter = col[0].column_letter  # ambil nama kolom (A, B, C, ...)
    for cell in col:
        try:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        except:
            pass
    adjusted_width = max_length + 2  # kasih extra space biar rapi
    ws.column_dimensions[col_letter].width = adjusted_width

wb.save(file_excel)

driver.quit()
