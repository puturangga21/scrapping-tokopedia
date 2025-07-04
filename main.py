from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from pymongo import MongoClient

# Inisialisasi koneksi MongoDB
MONGO_URI = 'mongodb+srv://puturangga21:abcd@cluster.67v0swb.mongodb.net/'
DATABASE_NAME = 'big_data'
COLLECTION_NAME = 'dataset_raw'

try:
  client = MongoClient(MONGO_URI)
  db = client[DATABASE_NAME]
  collection = db[COLLECTION_NAME]
  print(f"✅ Terkoneksi ke MongoDB: Database '{DATABASE_NAME}', Collection '{COLLECTION_NAME}'")
except Exception as e:
  print(f"[ERROR] Gagal terkoneksi ke MongoDB: {e}")
  exit()

# Konfigurasi driver
opsi = webdriver.ChromeOptions()
opsi.add_argument('--sandbox')
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

produk_list = []

# Buka halaman target
for page in range(51, 52):
  print(f"\n📄 Sedang membuka halaman {page}")
  target_url = f'https://www.tokopedia.com/search?page={page}&q=elektronik'
  driver.set_window_size(1300, 800)
  driver.get(target_url)

  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-5wh65g'))
    )
  except Exception as e:
    print(f"[ERROR] Gagal memuat produk di halaman {page}: {e}")
    continue 

  # Scroll untuk load semua produk
  for i in range(7):
    driver.execute_script(f'window.scrollBy(0, {800});')
    print(f"🔽 Scrolled {i+1}x")
    time.sleep(1)

  # Ambil produk di halaman ini
  raw_html = driver.page_source
  soup = BeautifulSoup(raw_html, 'html.parser')
  products = soup.find_all('div', class_='css-5wh65g')

  for product in products:
    a_tag = product.find('a', href=True)
    if not a_tag:
      print("[WARNING] Produk tidak memiliki tag <a>, dilewati.")
      continue

    product_link = a_tag['href']

    try:
      driver.get(product_link)
      WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-j63za0'))
      )
    except Exception as e:
      print(f"[ERROR] Gagal membuka halaman produk: {product_link} - {e}")
      continue

    # Klik deskripsi jika ada
    try:
      deskripsi_button = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="btnPDPSeeMore"]'))
      )
      deskripsi_button.click()
      time.sleep(2)
    except Exception as e:
      print(f"[WARNING] Deskripsi tidak ditemukan/klik gagal di produk: {product_link}")

    # Ambil detail
    raw_html_detail = driver.page_source
    soup_detail = BeautifulSoup(raw_html_detail, 'html.parser')

    title_el = soup_detail.find('h1', class_='css-j63za0')
    price_el = soup_detail.find('div', class_='price')
    original_price_el = soup_detail.find('div', class_='original-price')
    discount_el = soup_detail.find('div', class_='css-1c4ggdd')
    stock_el = soup_detail.find('p', class_='css-170i345-unf-heading e1qvo2ff8')
    delivery_el = soup_detail.find('h2', class_='css-793nib-unf-heading e1qvo2ff2')
    breadcrumb_nav = soup_detail.find('nav', {'aria-label': 'Breadcrumb'})

    product_title = title_el.text.strip() if title_el else "N/A"
    price = price_el.text.strip() if price_el else "N/A"
    original_price = original_price_el.text.split(' ')[3] if original_price_el else "N/A"
    amount_discount = discount_el.text.split(' ')[1] if discount_el else "N/A"
    stock = stock_el.text.strip() if stock_el else "N/A"
    delivery = delivery_el.text.strip() if delivery_el else "N/A"
    breadcrumb_items = breadcrumb_nav.find_all('li') if breadcrumb_nav else []

    # Pastikan breadcrumb cukup panjang
    if len(breadcrumb_items) >= 2:
        sub_category_el = breadcrumb_items[-2] 
        sub_category_text = sub_category_el.get_text(strip=True)
    else:
        sub_category_text = "N/A"

    produk_data = {
      "Title": product_title,
      "Price": price,
      "Original Price": original_price,
      "Discount": amount_discount,
      "Stock": stock,
      "Delivery": delivery,
      "Subcategory": sub_category_text
    }

    if product_title == "N/A":
      print(f"[WARNING] Produk tidak memiliki judul, dilewati")
      continue 

    produk_list.append(produk_data)

    # Simpan ke MongoDB
    try:
      collection.insert_one(produk_data)
      print("✅ Data produk berhasil disimpan ke MongoDB.")
    except Exception as e:
      print(f"[ERROR] Gagal menyimpan data ke MongoDB: {e}")

    print("✅ Produk ke -", len(produk_list), "berhasil disimpan.")
    print("=====================================")
    for k, v in produk_data.items():
        print(f"   {k}: {v}")

driver.quit()
df = pd.DataFrame(produk_list)
df.to_csv('produk_tokopedia_optimized.csv', index=False, sep=';', encoding='utf-8-sig')
print("✅ Semua data berhasil disimpan.")