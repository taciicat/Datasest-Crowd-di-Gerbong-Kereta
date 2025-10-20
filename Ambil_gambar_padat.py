from pathlib import Path
import os
from icrawler.builtin import BingImageCrawler

# Lokasi penyimpanan gambar
root = Path(r"C:\Users\sunri\Documents\Datasest-Crowd-di-Gerbong-Kereta\data\Gabungan")
os.makedirs(root, exist_ok=True)

# Daftar keyword pencarian - fokus pada kepadatan PADAT / RAMAI
keywords = [
    "crowded train interior",
    "packed subway carriage",
    "busy commuter train",
    "standing passengers in train",
    "crowded metro interior",
    "rush hour subway",
    "train full of passengers",
    "crowded light rail car",
    "standing passengers in metro",
    "fully occupied train seats",
    "crowded railway carriage",
    "busy bullet train interior",
    "rush hour train Japan",
    "passenger train fully packed",
    "dense crowd inside subway",
    "people standing tightly in train",
    "rush hour metro passengers",
    "overcrowded train cabin",
    "crowded underground train",
    "full train with no empty seats",
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

print("\nSelesai. Pengambilan gambar kategori 'PADAT' selesai!")
print(f"Semua gambar disimpan di: {root}")

