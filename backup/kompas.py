from bs4 import BeautifulSoup
import requests
import csv
import time

with open('kompas_scraped2.csv', 'w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['Title', 'Tag', 'Image URL', 'Article URL', 'Author', 'Date', 'Content'])

  for halaman in range(1, 70):
    print(f"\n--- Scraping Halaman {halaman} ---\n")

    url = f'https://indeks.kompas.com/?source=navbar&site=tren&page={halaman}'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    articles = soup.find_all('div', class_='articleItem')

    for article in articles:
      try:
        article_title = article.find('h2', class_='articleTitle').text
        article_tag = article.find('div', class_='articlePost-subtitle').text
        article_img = article.find('div', class_='articleItem-img').find('img')['src']
        more_info = article.find('a', 'article-link')['href']

        # scrap detail artikel
        detail_html = requests.get(more_info).text
        detail_soup = BeautifulSoup(detail_html, 'lxml')

        article_author = ', '.join([e.get_text(strip=True).strip(',') for e in detail_soup.select('div.credit-title-nameEditor')])
        article_date = detail_soup.find('div', class_='read__time').text.split('-')[-1].strip()
        article_content = '\n'.join([p.get_text(strip=True) for p in detail_soup.select('div.read__content div.clearfix p') if p.get_text(strip=True)])

        writer.writerow([
          article_title,
          article_tag,
          article_img,
          more_info,
          article_author,
          article_date,
          article_content
        ])
        print(f"✅ Tersimpan: {article_title}")
        time.sleep(0.5)
      
      except Exception as e:
        print(f"⚠️  Gagal mengambil data artikel: {e}")