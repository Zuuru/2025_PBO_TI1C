# konfigurasi.py
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_DB = 'wellness_tracker.db'
DB_PATH = os.path.join(BASE_DIR, NAMA_DB)

KATEGORI_AKTIVITAS = ["Kardio", "Angkat Beban", "Yoga", "Berjalan", "Berlari", "Berenang", "Lainnya"]
SKALA_SUASANA_ENERGI = [1, 2, 3, 4, 5] # 1: Sangat Buruk/Rendah, 5: Sangat Baik/Tinggi