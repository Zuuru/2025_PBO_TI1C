# model.py
import datetime

class PengukuranTubuh:
    def __init__(self, tanggal: datetime.date, berat_kg: float, tinggi_cm: float, id_pengukuran: int | None = None):
        self.id = id_pengukuran
        self.tanggal = tanggal
        self.berat_kg = float(berat_kg) if berat_kg > 0 else 0.0
        self.tinggi_cm = float(tinggi_cm) if tinggi_cm > 0 else 0.0
        if self.berat_kg <= 0: print(f"Peringatan: Berat badan {berat_kg}' harus positif.")
        if self.tinggi_cm <= 0: print(f"Peringatan: Tinggi badan {tinggi_cm}' harus positif.")

    def hitung_imt(self) -> float:
        if self.tinggi_cm > 0 and self.berat_kg > 0:
            tinggi_meter = self.tinggi_cm / 100
            return self.berat_kg / (tinggi_meter ** 2)
        return 0.0

    def to_dict(self) -> dict:
        return {
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "berat_kg": self.berat_kg,
            "tinggi_cm": self.tinggi_cm
        }

class AktivitasFisik:
    def __init__(self, tanggal: datetime.date, jenis_aktivitas: str, durasi_menit: int, kalori_terbakar_perkiraan: float | None = None, catatan: str | None = None, id_aktivitas: int | None = None):
        self.id = id_aktivitas
        self.tanggal = tanggal
        self.jenis_aktivitas = jenis_aktivitas if jenis_aktivitas else "Lainnya"
        self.durasi_menit = int(durasi_menit) if durasi_menit > 0 else 0
        self.kalori_terbakar_perkiraan = float(kalori_terbakar_perkiraan) if kalori_terbakar_perkiraan is not None and kalori_terbakar_perkiraan >= 0 else None
        self.catatan = catatan
        if self.durasi_menit <= 0: print(f"Peringatan: Durasi aktivitas {durasi_menit}' harus positif.")

    def to_dict(self) -> dict:
        return {
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "jenis_aktivitas": self.jenis_aktivitas,
            "durasi_menit": self.durasi_menit,
            "kalori_terbakar_perkiraan": self.kalori_terbakar_perkiraan,
            "catatan": self.catatan
        }

class AsupanMakanan:
    def __init__(self, tanggal: datetime.date, deskripsi_makanan: str, kalori: float, protein_g: float | None = None, karbo_g: float | None = None, lemak_g: float | None = None, id_makanan: int | None = None):
        self.id = id_makanan
        self.tanggal = tanggal
        self.deskripsi_makanan = deskripsi_makanan
        self.kalori = float(kalori) if kalori >= 0 else 0.0
        self.protein_g = float(protein_g) if protein_g is not None and protein_g >= 0 else 0.0
        self.karbo_g = float(karbo_g) if karbo_g is not None and karbo_g >= 0 else 0.0
        self.lemak_g = float(lemak_g) if lemak_g is not None and lemak_g >= 0 else 0.0
        if self.kalori < 0: print(f"Peringatan: Kalori {kalori}' tidak boleh negatif.")

    def to_dict(self) -> dict:
        return {
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "deskripsi_makanan": self.deskripsi_makanan,
            "kalori": self.kalori,
            "protein_g": self.protein_g,
            "karbo_g": self.karbo_g,
            "lemak_g": self.lemak_g
        }

class AsupanAir:
    def __init__(self, tanggal: datetime.date, jumlah_ml: int, id_air: int | None = None):
        self.id = id_air
        self.tanggal = tanggal
        self.jumlah_ml = int(jumlah_ml) if jumlah_ml > 0 else 0
        if self.jumlah_ml <= 0: print(f"Peringatan: Jumlah air {jumlah_ml}' harus positif.")

    def to_dict(self) -> dict:
        return {
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "jumlah_ml": self.jumlah_ml
        }

class CatatanHarian:
    def __init__(self, tanggal: datetime.date, suasana_hati_skala: int | None = None, tingkat_energi_skala: int | None = None, catatan_tambahan: str | None = None, id_catatan: int | None = None):
        self.id = id_catatan
        self.tanggal = tanggal
        self.suasana_hati_skala = int(suasana_hati_skala) if suasana_hati_skala is not None and 1 <= suasana_hati_skala <= 5 else None
        self.tingkat_energi_skala = int(tingkat_energi_skala) if tingkat_energi_skala is not None and 1 <= tingkat_energi_skala <= 5 else None
        self.catatan_tambahan = catatan_tambahan
        if self.suasana_hati_skala is not None and not (1 <= self.suasana_hati_skala <= 5): print(f"Peringatan: Skala suasana hati {suasana_hati_skala}' harus antara 1 dan 5.")
        if self.tingkat_energi_skala is not None and not (1 <= self.tingkat_energi_skala <= 5): print(f"Peringatan: Skala tingkat energi {tingkat_energi_skala}' harus antara 1 dan 5.")

    def to_dict(self) -> dict:
        return {
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "suasana_hati_skala": self.suasana_hati_skala,
            "tingkat_energi_skala": self.tingkat_energi_skala,
            "catatan_tambahan": self.catatan_tambahan
        }