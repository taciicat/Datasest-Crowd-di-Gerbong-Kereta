from pathlib import Path
import os
from icrawler.builtin import BingImageCrawler

# Lokasi penyimpanan gambar
root = Path(r"C:\Users\sunri\Documents\Datasest-Crowd-di-Gerbong-Kereta\data\Gabungan")
os.makedirs(root, exist_ok=True)

# Daftar keyword pencarian
keywords = [
  "moderately crowded train interior",
    "medium crowded subway carriage",
    "average crowded train seats",
    "passengers sitting and standing train",
    "moderate occupancy commuter train",
    "some passengers inside metro carriage",
    "medium crowded light rail car",
    "train with moderate number of passengers",
    "half full railway interior",
    "commuter train with seated passengers",
    "train with standing and seated passengers",
    "moderate transit car occupancy",
    "not crowded bullet train interior",
    "passenger train with some empty seats",
    "normal rush hour metro",
    "average occupancy train carriage",
    "subway with seated and few standing passengers",
    "medium full japan train interior",
    "moderately filled train cabin",
    "train cabin with normal crowd level",
    ]

# Jumlah maksimum gambar per keyword
max_per_keyword = 25  # 20 kata kunci * 25 = 500 gambar

# Unduh semua gambar ke satu folder (tanpa subfolder per keyword)
for keyword in keywords:
    print(f"\nMencari dan mengunduh gambar untuk: {keyword}")
    try:
        # Hitung jumlah file yang sudah ada agar indeks file berlanjut
        existing = [p for p in root.glob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}]
        offset = len(existing)

        # Buat crawler baru per keyword agar limit max_num berlaku per keyword
        crawler = BingImageCrawler(storage={"root_dir": str(root)})
        crawler.crawl(keyword=keyword, max_num=max_per_keyword, file_idx_offset=offset)
    except Exception as e:
        print(f"Gagal mengunduh untuk '{keyword}': {e}")

print("\nSelesai. Pengambilan gambar selesai!")
print(f"Semua gambar disimpan di: {root}")
