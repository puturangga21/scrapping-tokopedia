from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Konfigurasi driver
opsi = webdriver.ChromeOptions()
opsi.add_argument('--no-sandbox')  
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

produk_list = []

# Buka halaman target
for page in range(1, 2):
  print(f"\n📄 Sedang membuka halaman {page}")
  target_url = f'https://www.tokopedia.com/search?page={page}&q=elektronik'
  driver.set_window_size(1300, 800)
  driver.get(target_url)
  time.sleep(6)

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
    product_link = product.find('a', href=True)['href']
    
    # Mengunjungi halaman produk
    print(f"🔗 Mengunjungi: {product_link}")
    driver.get(product_link)
    time.sleep(6)

    # Klik deskripsi jika ada
    try:
      deskripsi_button = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="btnPDPSeeMore"]'))
      )
      deskripsi_button.click()
      # print("✅ Tombol 'Lihat Selengkapnya' berhasil diklik.")
      time.sleep(2)
    except:
      print("❌ Gagal menemukan atau mengklik tombol deskripsi.")

    # Ambil detail
    raw_html_detail = driver.page_source
    soup_detail = BeautifulSoup(raw_html_detail, 'html.parser')

    title_el = soup_detail.find('h1', class_='css-j63za0')
    price_el = soup_detail.find('div', class_='price')
    original_price_el = soup_detail.find('div', class_='original-price')
    discount_el = soup_detail.find('div', class_='css-1c4ggdd')
    stock_el = soup_detail.find('p', class_='css-101ywxy-unf-heading e1qvo2ff8')
    delivery_el = soup_detail.find('h2', class_='css-g78l6p-unf-heading e1qvo2ff2')

    product_title = title_el.text.strip() if title_el else "N/A"
    price = price_el.text.strip() if price_el else "N/A"
    original_price = original_price_el.text.split(' ')[3] if original_price_el else "N/A"
    amount_discount = discount_el.text.split(' ')[1] if discount_el else "N/A"
    stock = stock_el.text.strip() if stock_el else "N/A"
    delivery = delivery_el.text.strip() if delivery_el else "N/A"

    produk_data = {
      "Title": product_title,
      "Price": price,
      "Original Price": original_price,
      "Discount": amount_discount,
      "Stock": stock,
      "Delivery": delivery
    }

    if product_title == "N/A":
      print("⚠️  Produk tidak memiliki judul, dilewati.")
      continue 

    produk_list.append(produk_data)

    print("✅ Produk ke -", len(produk_list), "berhasil disimpan.")
    print("=====================================")
    for k, v in produk_data.items():
        print(f"   {k}: {v}")

driver.quit()
df = pd.DataFrame(produk_list)
df.to_csv('produk_tokopedia_allpages.csv', index=False, encoding='utf-8-sig')
print("✅ Semua data berhasil disimpan.")