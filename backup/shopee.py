from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# konfigurasi driver
opsi = webdriver.ChromeOptions()
opsi.add_argument('--sandbox')
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

# 1. Buka halaman target
target_url = 'https://www.tokopedia.com/search?page=1&q=macbook'
driver.set_window_size(1300, 800)
driver.get(target_url)
time.sleep(6)

# 2. Scroll untuk load semua produk
scroll_pause = 2
scroll_count = 8
scroll_step = 800

for i in range(scroll_count):
    driver.execute_script(f'window.scrollBy(0, {scroll_step});')
    print(f"🔽 Scrolled {i+1}x")
    time.sleep(scroll_pause)

# 3. Ambil semua produk di halaman
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_areas = soup.find_all('div', class_='css-5wh65g')

produk_list = []

# 4. Loop setiap produk
for idx, product in enumerate(product_areas):
  try:
    product_link = product.find('a', href=True)['href']
    print(f"[{idx+1}] Mengunjungi: {product_link}")
    driver.get(product_link)
    time.sleep(5)

    # Klik tombol "Lihat Selengkapnya"
    try:
      deskripsi_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="btnPDPSeeMore"]'))
      )
      deskripsi_button.click()
      print("✅ Tombol 'Lihat Selengkapnya' berhasil diklik.")
      time.sleep(2)
    except:
      print("❌ Gagal menemukan atau mengklik tombol deskripsi.")

    # Ambil konten detail
    detail_parser_content = BeautifulSoup(driver.page_source, 'html.parser')

    product_title = detail_parser_content.find('h1', class_='css-j63za0').text 
    price = detail_parser_content.find('div', class_='price').text 
    original_price = detail_parser_content.find('div', class_='original-price').text.split(' ')[3]
    amount_discount = detail_parser_content.find('div', class_='css-1c4ggdd').text.split(' ')[1]
    stock = detail_parser_content.find('p', class_='css-101ywxy-unf-heading e1qvo2ff8').text
    description = detail_parser_content.find('span', class_='css-168ydy0 eytdjj01').text
    delivery = detail_parser_content.find('h2', class_='css-g78l6p-unf-heading e1qvo2ff2').text

    produk_data = {
        "Title": product_title if product_title else "N/A",
        "Price": price if price else "N/A" ,
        "Original Price": original_price if original_price else "N/A",
        "Discount": amount_discount if amount_discount else "N/A",
        "Stock": stock if stock else "N/A",
        "Description": description if description else "N/A",
        "Delivery": delivery if delivery else "N/A",
        "Link": product_link
    }

    produk_list.append(produk_data)

    # 🖨️ Print hasil data produk ke-console
    print(f"✅ Data Produk {idx+1}:")
    for k, v in produk_data.items():
        print(f"   {k}: {v}")
    
  except Exception as e:
    print(f"❌ Gagal mengambil produk ke-{idx+1}: {e}")

# 5. Simpan ke CSV
df = pd.DataFrame(produk_list)
df.to_csv("tokopedia_produk_page1.csv", index=False, encoding='utf-8-sig')

driver.quit()