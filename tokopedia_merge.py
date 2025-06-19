import pandas as pd
import glob

# Ambil semua file CSV yang namanya sesuai pola
csv_files = glob.glob("./dataset/produk_tokopedia_*.csv")

# Gabungkan semua file menjadi satu DataFrame
df_list = [pd.read_csv(file, delimiter=';') for file in csv_files]
df_all = pd.concat(df_list, ignore_index=True)

# Simpan hasil gabungan
df_all.to_csv("produk_tokopedia_merge.csv", index=False, sep=';')
print("✅ Semua file berhasil digabungkan.")
