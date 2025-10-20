from pathlib import Path
import os
from icrawler.builtin import BingImageCrawler

# Lokasi penyimpanan gambar
root = Path(r"C:\Users\sunri\Documents\Datasest-Crowd-di-Gerbong-Kereta\data\Gabungan")
os.makedirs(root, exist_ok=True)

# Daftar keyword pencarian
keywords = [
    "empty train interior",
    "empty subway carriage",
    "empty train seats",
    "inside empty passenger car",
    "empty commuter train",
    "empty metro carriage",
    "empty light rail car",
    "train empty cabin",
    "empty railway interior",
    "train with no passengers",
    "empty transit car",
    "empty bullet train interior",
    "empty metro station platform",
    "empty passenger train coach",
    "inside clean train cabin",
    "empty underground train",
    "train carriage daylight",
    "empty japan train interior",
    "minimalist train interior",
    "quiet train cabin",
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
