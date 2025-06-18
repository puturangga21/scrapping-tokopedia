import pandas as pd
import re

def preprocess_price_columns(file_path, output_path):
  df = pd.read_csv(file_path, sep=';')

  # Normalisasi nama kolom
  df.columns = df.columns.str.strip().str.lower()

  # Normalisasi isi kolom
  df['original price'] = df['original price'].fillna('N/A').astype(str).str.strip()
  df['discount'] = df['discount'].fillna('N/A').astype(str).str.strip()
  df['price'] = df['price'].astype(str).str.strip()
  
  # Hilangkan "Rp" dan titik pada kolom price dan original price
  df['price'] = df['price'].str.replace('Rp', '', case=False, regex=False).str.replace('.', '', regex=False).str.strip()
  df['original price'] = df['original price'].str.replace('Rp', '', case=False, regex=False).str.replace('.', '', regex=False).str.strip()

  # Ganti original price jika isinya 'N/A'
  df['original price'] = df.apply(
      lambda row: row['price'] if row['original price'] == 'N/A' else row['original price'],
      axis=1
  )

  # Konversi kolom discount ke numerik
  df['discount'] = df['discount'].replace('', '0')
  df['discount'] = df['discount'].str.replace('%', '', regex=False).str.strip()
  df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)

  # Preprocessing kolom stock → ambil hanya angka
  df['stock'] = df['stock'].apply(lambda x: re.findall(r'\d+', x))
  df['stock'] = df['stock'].apply(lambda x: int(x[0]) if x else 0)

  # Preprocessing kolom delivery → hapus "Dikirim dari" dan ambil kota
  df['delivery'] = df['delivery'].str.replace('Dikirim dari', '', case=False, regex=False).str.strip()

  df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
  print(f"✅ Preprocessed file saved to {output_path}")

preprocess_price_columns("dataset/produk_tokopedia_merge.csv", "dataset/produk_tokopedia_cleaned.csv")
