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
opsi.add_argument('--sandbox')
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

target_url = f'https://www.tokopedia.com/bu-phone-casing/jam-alarm-elektronik-led-suhu-jam-alarm-cermin-pengisian-daya-ponsel-usb-1729743397930698010?extParam=ivf%3Dfalse%26keyword%3Delektronik%26search_id%3D20250618120521357A6FDF7642BF382JLV%26src%3Dsearch'
driver.set_window_size(1300, 800)
driver.get(target_url)

raw_html_detail = driver.page_source
soup_detail = BeautifulSoup(raw_html_detail, 'html.parser')

title_el = soup_detail.find('h1', class_='css-j63za0')
price_el = soup_detail.find('div', class_='price')
original_price_el = soup_detail.find('div', class_='original-price')
discount_el = soup_detail.find('div', class_='css-1c4ggdd')
stock_el = soup_detail.find('p', class_='css-101ywxy-unf-heading e1qvo2ff8')
delivery_el = soup_detail.find('h2', class_='css-g78l6p-unf-heading e1qvo2ff2')
breadcrumb_nav = soup_detail.find('nav', {'aria-label': 'Breadcrumb'})

breadcrumb_items = breadcrumb_nav.find_all('li') if breadcrumb_nav else []
product_title = title_el.text.strip() if title_el else "N/A"
price = price_el.text.strip() if price_el else "N/A"
original_price = original_price_el.text.split(' ')[3] if original_price_el else "N/A"
amount_discount = discount_el.text.split(' ')[1] if discount_el else "N/A"
stock = stock_el.text.strip() if stock_el else "N/A"
delivery = delivery_el.text.strip() if delivery_el else "N/A"

# Pastikan breadcrumb cukup panjang
if len(breadcrumb_items) >= 2:
    sub_category_el = breadcrumb_items[-2]  # Elemen terakhir dikurang 1
    sub_category_text = sub_category_el.get_text(strip=True)
else:
    sub_category_text = "N/A"

print(product_title)
print(price)
print(original_price)
print(amount_discount)
print(stock)
print(delivery)
print(sub_category_text)
