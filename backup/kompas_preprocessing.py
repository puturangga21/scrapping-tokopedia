import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Fungsi membersihkan teks
def clean_text(text):
  if pd.isna(text):
      return ""
  text = BeautifulSoup(text, "html.parser").get_text()              # Hapus tag HTML
  text = re.sub(r'^KOMPAS\.com-\s*', '', text)                      # Hapus awalan
  text = text.lower()                                               # Lowercase
  text = re.sub(r'[^a-z0-9\s,.]', '', text)                         # Hapus karakter aneh
  text = re.sub(r'\s+', ' ', text).strip()                          # Normalisasi spasi
  return text

# Fungsi ubah format tanggal ke datetime
def convert_date(date_str):
  try:
    date_cleaned = re.sub(r'\s*WIB$', '', date_str.strip())
    return datetime.strptime(date_cleaned, "%d/%m/%Y, %H:%M")
  except Exception:
    return pd.NaT 

def preprocess_csv(file_path, output_path):
  df = pd.read_csv(file_path)

  # Preprocessing teks
  df['Content'] = df['Content'].apply(clean_text)
  df['Title'] = df['Title'].apply(clean_text)
  df['Tag'] = df['Tag'].apply(clean_text)

  # Preprocessing tanggal
  df['Date'] = df['Date'].apply(convert_date)

  # Simpan
  df.to_csv(output_path, index=False)
  print(f"Preprocessed file saved to {output_path}")


preprocess_csv("kompas_scraped.csv", "kompas_cleaned.csv")
