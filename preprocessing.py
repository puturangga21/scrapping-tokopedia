import pandas as pd
import re
from pymongo import MongoClient

def preprocess_mongo():
  MONGO_URI = 'mongodb+srv://puturangga21:abcd@cluster.67v0swb.mongodb.net/'
  DATABASE_NAME = 'big_data'
  SOURCE_COLLECTION_NAME = 'dataset_raw'
  DESTINATION_COLLECTION_NAME = 'dataset_tokopedia'

  client = None

  try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    source_collection = db[SOURCE_COLLECTION_NAME]
    destination_collection = db[DESTINATION_COLLECTION_NAME]
    print(f"✅ Terkoneksi ke MongoDB: Database '{DATABASE_NAME}'")
  except Exception as e:
    print(f"[ERROR] Gagal terkoneksi ke MongoDB: {e}")
    if client:
        client.close()
    return # Keluar jika gagal terkoneksi

  # 1. Ambil data dari MongoDB (collection dataset_test)
  print(f"🔄 Mengambil data dari koleksi sumber: '{SOURCE_COLLECTION_NAME}'...")
  data_from_mongo_raw = list(source_collection.find({}))

  # Hapus field '_id' karena akan dibuat ulang saat insert ke koleksi baru
  # Ini penting untuk mencegah DuplicateKeyError jika Anda menginsert ke collection baru
  # yang mungkin sudah ada atau jika Anda ingin ID baru.
  data_for_df = []
  for doc in data_from_mongo_raw:
    doc_copy = doc.copy()
    if '_id' in doc_copy:
      del doc_copy['_id']
    data_for_df.append(doc_copy)

  df = pd.DataFrame(data_for_df)
  print(f"✅ Berhasil mengambil {len(df)} dokumen dari MongoDB.")

  if df.empty:
    print("⚠️ Data kosong dari koleksi sumber. Tidak ada preprocessing yang dilakukan.")
    client.close()
    return

  # Normalisasi nama kolom
  df.columns = df.columns.str.strip().str.lower()

  # Normalisasi isi kolom
  df['original price'] = df['original price'].fillna('N/A').astype(str).str.strip()
  df['discount'] = df['discount'].fillna('N/A').astype(str).str.strip()
  df['price'] = df['price'].astype(str).str.strip()
  df['stock'] = df['stock'].fillna('').astype(str)
  
  # Hilangkan "Rp" dan titik pada kolom price dan original price
  df['price'] = df['price'].str.replace('Rp', '', case=False, regex=False).str.replace('.', '', regex=False).str.strip()
  df['original price'] = df['original price'].str.replace('Rp', '', case=False, regex=False).str.replace('.', '', regex=False).str.strip()

  # Ganti original price jika isinya 'N/A'
  df['original price'] = df.apply(
    lambda row: row['price'] if row['original price'] == 'N/A' else row['original price'],
    axis=1
  )

  df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
  df['original price'] = pd.to_numeric(df['original price'], errors='coerce').fillna(0).astype(int)

  # Konversi kolom discount ke numerik
  df['discount'] = df['discount'].replace('', '0')
  df['discount'] = df['discount'].str.replace('%', '', regex=False).str.strip()
  df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0).astype(int)

  # Preprocessing kolom stock → ambil hanya angka
  df['stock'] = df['stock'].apply(lambda x: re.findall(r'\d+', x))
  df['stock'] = df['stock'].apply(lambda x: int(x[0]) if x else 0)

  # Preprocessing kolom delivery → hapus "Dikirim dari" dan ambil kota
  df['delivery'] = df['delivery'].str.replace('Dikirim dari', '', case=False, regex=False).str.strip()

  print("✅ Preprocessing selesai.")

  # 2. Simpan kembali hasil preprocessing ke MongoDB
  print(f"🔄 Menyimpan hasil preprocessing ke koleksi tujuan: '{DESTINATION_COLLECTION_NAME}'...")
  # Konversi DataFrame kembali ke list of dictionaries
  preprocessed_data = df.to_dict(orient='records')

  if preprocessed_data:
    try:
      # Opsional: Jika Anda ingin menghapus semua dokumen lama di koleksi tujuan
      # sebelum menyisipkan yang baru, aktifkan baris di bawah ini:
      # destination_collection.delete_many({})
      # print(f"Menghapus data lama dari koleksi '{DESTINATION_COLLECTION_NAME}'.")
      destination_collection.insert_many(preprocessed_data)
      print(f"✅ Berhasil menyimpan {len(preprocessed_data)} dokumen ke MongoDB di koleksi '{DESTINATION_COLLECTION_NAME}'.")
    except Exception as e:
      print(f"[ERROR] Gagal menyimpan data ke MongoDB: {e}")
  else:
    print("⚠️ Tidak ada data untuk disimpan setelah preprocessing.")

  # Tutup koneksi MongoDB
  if client:
    client.close()
  print("Koneksi MongoDB ditutup.")

preprocess_mongo()
