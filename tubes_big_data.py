import pandas as pd
import matplotlib.pyplot as plt
import textwrap

"""# Analisis 1: **Produk dengan Diskon Tertinggi**"""

# Load data
df = pd.read_csv('dataset/produk_tokopedia_cleaned.csv', delimiter=';')

# Hitung diskon dalam rupiah
df['diskon_rupiah'] = df['original price'] - df['price']

# Filter hanya produk dengan diskon
df_diskon = df[df['diskon_rupiah'] > 0]

# Ambil produk dengan diskon rupiah terbesar
top_diskon = df_diskon.sort_values(by='diskon_rupiah', ascending=False).head(10).reset_index(drop=True)

# Wrap nama produk agar tidak terlalu panjang di grafik
wrapped_titles = [textwrap.fill(title, 45) for title in top_diskon['title']]

# Setup plot dengan ukuran lebih tinggi
plt.figure(figsize=(14, 8))
bars = plt.barh(wrapped_titles, top_diskon['diskon_rupiah'], color='#A0C878')

# Balikkan urutan
plt.gca().invert_yaxis()

# Label sumbu dan judul
plt.xlabel('Jumlah Diskon (Rp)')
plt.title('Produk dengan Diskon Terbesar\n(Rp, Persen, dan Lokasi)', fontsize=14)

# Tambahkan label: Rp, %, dan lokasi
for i, bar in enumerate(bars):
    width = bar.get_width()
    persen = top_diskon.loc[i, 'discount']
    lokasi = top_diskon.loc[i, 'delivery']
    label_text = f"Rp{int(width):,} ({persen}%)\n{lokasi}"
    plt.text(width + max(top_diskon['diskon_rupiah']) * 0.01,
             bar.get_y() + bar.get_height()/2,
             label_text, va='center', fontsize=9)

plt.tight_layout()
plt.show()