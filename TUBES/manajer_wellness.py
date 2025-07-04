# manajer_wellness.py
import datetime
import pandas as pd
import database
from model import PengukuranTubuh, AktivitasFisik, AsupanMakanan, AsupanAir, CatatanHarian

class WellnessTracker:
    _db_setup_done = False # Flag untuk memastikan setup DB hanya dicek sekali per sesi

    def __init__(self):
        if not WellnessTracker._db_setup_done:
            print("[WellnessTracker] Melakukan pengecekan/setup database awal...")
            if database.setup_database_initial():
                WellnessTracker._db_setup_done = True
                print("[WellnessTracker] Database siap.")
            else:
                print("[WellnessTracker] KRITICAL: Setup database awal GAGAL!")

    # --- Pengukuran Tubuh ---
    def tambah_pengukuran(self, pengukuran: PengukuranTubuh) -> bool:
        if not isinstance(pengukuran, PengukuranTubuh) or pengukuran.berat_kg <= 0 or pengukuran.tinggi_cm <= 0:
            return False
        sql = "INSERT INTO pengukuran_tubuh (tanggal, berat_kg, tinggi_cm) VALUES (?, ?, ?)"
        params = (pengukuran.tanggal.strftime("%Y-%m-%d"), pengukuran.berat_kg, pengukuran.tinggi_cm)
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            pengukuran.id = last_id
            return True
        return False

    def get_riwayat_pengukuran(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT id, tanggal, berat_kg, tinggi_cm FROM pengukuran_tubuh"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['IMT'] = df.apply(lambda row: PengukuranTubuh(row['tanggal'], row['berat_kg'], row['tinggi_cm']).hitung_imt(), axis=1)
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            df['Berat (kg)'] = df['berat_kg'].map('{:.1f}'.format)
            df['Tinggi (cm)'] = df['tinggi_cm'].map('{:.0f}'.format)
            df['IMT'] = df['IMT'].map('{:.2f}'.format)
            df = df[['id', 'Tanggal', 'Berat (kg)', 'Tinggi (cm)', 'IMT']]
        return df

    def hapus_pengukuran(self, id_pengukuran: int) -> bool:
        sql = "DELETE FROM pengukuran_tubuh WHERE id = ?"
        return database.execute_query(sql, (id_pengukuran,)) is not None

    # --- Aktivitas Fisik ---
    def tambah_aktivitas(self, aktivitas: AktivitasFisik) -> bool:
        if not isinstance(aktivitas, AktivitasFisik) or aktivitas.durasi_menit <= 0:
            return False
        sql = "INSERT INTO aktivitas_fisik (tanggal, jenis_aktivitas, durasi_menit, kalori_terbakar) VALUES (?, ?, ?, ?)"
        params = (aktivitas.tanggal.strftime("%Y-%m-%d"), aktivitas.jenis_aktivitas, aktivitas.durasi_menit, aktivitas.kalori_terbakar_perkiraan)
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            aktivitas.id = last_id
            return True
        return False

    def get_riwayat_aktivitas(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT id, tanggal, jenis_aktivitas, durasi_menit, kalori_terbakar FROM aktivitas_fisik"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            df['Durasi (menit)'] = df['durasi_menit']
            df['Kalori Terbakar'] = df['kalori_terbakar'].fillna(0).map('{:.0f}'.format)
            df = df[['id', 'Tanggal', 'jenis_aktivitas', 'Durasi (menit)', 'Kalori Terbakar']]
            df.rename(columns={'jenis_aktivitas': 'Jenis Aktivitas'}, inplace=True)
        return df

    def hapus_aktivitas(self, id_aktivitas: int) -> bool:
        sql = "DELETE FROM aktivitas_fisik WHERE id = ?"
        return database.execute_query(sql, (id_aktivitas,)) is not None

    # --- Asupan Makanan ---
    def tambah_makanan(self, makanan: AsupanMakanan) -> bool:
        if not isinstance(makanan, AsupanMakanan) or not makanan.deskripsi_makanan or makanan.kalori < 0:
            return False
        sql = "INSERT INTO asupan_makanan (tanggal, deskripsi_makanan, kalori, protein_g, karbo_g, lemak_g) VALUES (?, ?, ?, ?, ?, ?)"
        params = (makanan.tanggal.strftime("%Y-%m-%d"), makanan.deskripsi_makanan, makanan.kalori, makanan.protein_g, makanan.karbo_g, makanan.lemak_g)
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            makanan.id = last_id
            return True
        return False

    def get_riwayat_makanan(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT id, tanggal, deskripsi_makanan, kalori, protein_g, karbo_g, lemak_g FROM asupan_makanan"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            df['Kalori'] = df['kalori'].map('{:.0f}'.format)
            df['Protein (g)'] = df['protein_g'].fillna(0).map('{:.1f}'.format)
            df['Karbo (g)'] = df['karbo_g'].fillna(0).map('{:.1f}'.format)
            df['Lemak (g)'] = df['lemak_g'].fillna(0).map('{:.1f}'.format)
            df = df[['id', 'Tanggal', 'deskripsi_makanan', 'Kalori', 'Protein (g)', 'Karbo (g)', 'Lemak (g)']]
            df.rename(columns={'deskripsi_makanan': 'Deskripsi Makanan'}, inplace=True)
        return df

    def hapus_makanan(self, id_makanan: int) -> bool:
        sql = "DELETE FROM asupan_makanan WHERE id = ?"
        return database.execute_query(sql, (id_makanan,)) is not None

    # --- Asupan Air ---
    def tambah_air(self, air: AsupanAir) -> bool:
        if not isinstance(air, AsupanAir) or air.jumlah_ml <= 0:
            return False
        sql = "INSERT INTO asupan_air (tanggal, jumlah_ml) VALUES (?, ?)"
        params = (air.tanggal.strftime("%Y-%m-%d"), air.jumlah_ml)
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            air.id = last_id
            return True
        return False

    def get_riwayat_air(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT id, tanggal, jumlah_ml FROM asupan_air"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            df['Jumlah (ml)'] = df['jumlah_ml']
            df = df[['id', 'Tanggal', 'Jumlah (ml)']]
        return df

    def hapus_air(self, id_air: int) -> bool:
        sql = "DELETE FROM asupan_air WHERE id = ?"
        return database.execute_query(sql, (id_air,)) is not None

    # --- Catatan Harian ---
    def tambah_catatan(self, catatan: CatatanHarian) -> bool:
        if not isinstance(catatan, CatatanHarian):
            return False
        sql = "INSERT INTO catatan_harian (tanggal, suasana_hati_skala, tingkat_energi_skala, catatan_tambahan) VALUES (?, ?, ?, ?)"
        params = (catatan.tanggal.strftime("%Y-%m-%d"), catatan.suasana_hati_skala, catatan.tingkat_energi_skala, catatan.catatan_tambahan)
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            catatan.id = last_id
            return True
        return False

    def get_riwayat_catatan(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT id, tanggal, suasana_hati_skala, tingkat_energi_skala, catatan_tambahan FROM catatan_harian"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d-%m-%Y')
            df['Suasana Hati (1-5)'] = df['suasana_hati_skala'].fillna('N/A').astype(str)
            df['Tingkat Energi (1-5)'] = df['tingkat_energi_skala'].fillna('N/A').astype(str)
            df.rename(columns={'catatan_tambahan': 'Catatan Tambahan'}, inplace=True)
            df = df[['id', 'Tanggal', 'Suasana Hati (1-5)', 'Tingkat Energi (1-5)', 'Catatan Tambahan']]
        return df

    def hapus_catatan(self, id_catatan: int) -> bool:
        sql = "DELETE FROM catatan_harian WHERE id = ?"
        return database.execute_query(sql, (id_catatan,)) is not None

    # --- Ringkasan & Analisis ---
    def hitung_total_kalori_harian(self, tanggal: datetime.date) -> tuple[float, float]:
        sql_makanan = "SELECT SUM(kalori) FROM asupan_makanan WHERE tanggal = ?"
        kalori_makanan = database.fetch_query(sql_makanan, (tanggal.strftime("%Y-%m-%d"),), fetch_all=False)
        total_kalori_makanan = float(kalori_makanan[0]) if kalori_makanan and kalori_makanan[0] is not None else 0.0

        sql_aktivitas = "SELECT SUM(kalori_terbakar) FROM aktivitas_fisik WHERE tanggal = ?"
        kalori_aktivitas = database.fetch_query(sql_aktivitas, (tanggal.strftime("%Y-%m-%d"),), fetch_all=False)
        total_kalori_terbakar = float(kalori_aktivitas[0]) if kalori_aktivitas and kalori_aktivitas[0] is not None else 0.0

        return total_kalori_makanan, total_kalori_terbakar

    def hitung_total_air_harian(self, tanggal: datetime.date) -> float:
        sql_air = "SELECT SUM(jumlah_ml) FROM asupan_air WHERE tanggal = ?"
        air_masuk = database.fetch_query(sql_air, (tanggal.strftime("%Y-%m-%d"),), fetch_all=False)
        return float(air_masuk[0]) if air_masuk and air_masuk[0] is not None else 0.0

    def get_latest_imt(self) -> tuple[float, datetime.date] | None:
        query = "SELECT tanggal, berat_kg, tinggi_cm FROM pengukuran_tubuh ORDER BY tanggal DESC, id DESC LIMIT 1"
        latest_data = database.fetch_query(query, fetch_all=False)
        if latest_data:
            pengukuran = PengukuranTubuh(latest_data['tanggal'], latest_data['berat_kg'], latest_data['tinggi_cm'])
            return pengukuran.hitung_imt(), pengukuran.tanggal
        return None

    def get_ringkasan_makro(self, tanggal: datetime.date) -> dict:
        query = """
        SELECT SUM(protein_g) as total_protein,
               SUM(karbo_g) as total_karbo,
               SUM(lemak_g) as total_lemak
        FROM asupan_makanan
        WHERE tanggal = ?
        """
        result = database.fetch_query(query, (tanggal.strftime("%Y-%m-%d"),), fetch_all=False)
        if result:
            return {
                "protein": float(result['total_protein']) if result['total_protein'] is not None else 0.0,
                "karbo": float(result['total_karbo']) if result['total_karbo'] is not None else 0.0,
                "lemak": float(result['total_lemak']) if result['total_lemak'] is not None else 0.0
            }
        return {"protein": 0.0, "karbo": 0.0, "lemak": 0.0}

    def get_data_tren_berat_badan(self, periode: str = "mingguan") -> pd.DataFrame:
        if periode == "mingguan":
            sql = """
            SELECT
                strftime('%Y-%W', tanggal) as periode,
                AVG(berat_kg) as avg_berat_kg
            FROM pengukuran_tubuh
            GROUP BY periode
            ORDER BY periode ASC
            """
        elif periode == "bulanan":
            sql = """
            SELECT
                strftime('%Y-%m', tanggal) as periode,
                AVG(berat_kg) as avg_berat_kg
            FROM pengukuran_tubuh
            GROUP BY periode
            ORDER BY periode ASC
            """
        else: # Harian
            sql = """
            SELECT
                tanggal as periode,
                berat_kg
            FROM pengukuran_tubuh
            ORDER BY tanggal ASC
            """
        df = database.get_dataframe(sql)
        if not df.empty:
            if periode == "harian":
                df['periode'] = pd.to_datetime(df['periode'])
                df.rename(columns={'berat_kg': 'Berat Badan (kg)'}, inplace=True)
            else:
                df['periode'] = df['periode'].apply(lambda x: f"Pekan {x.split('-')[1]}-{x.split('-')[0]}" if periode == "mingguan" else f"Bulan {x.split('-')[1]}-{x.split('-')[0]}")
                df.rename(columns={'avg_berat_kg': 'Berat Badan Rata-rata (kg)'}, inplace=True)
        return df

    def get_kalori_aktivitas_per_jenis(self, filter_tanggal_awal: datetime.date | None = None, filter_tanggal_akhir: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT jenis_aktivitas, SUM(kalori_terbakar) as total_kalori FROM aktivitas_fisik WHERE kalori_terbakar IS NOT NULL"
        params = []
        if filter_tanggal_awal and filter_tanggal_akhir:
            query += " AND tanggal BETWEEN ? AND ?"
            params.append(filter_tanggal_awal.strftime("%Y-%m-%d"))
            params.append(filter_tanggal_akhir.strftime("%Y-%m-%d"))
        elif filter_tanggal_awal:
            query += " AND tanggal >= ?"
            params.append(filter_tanggal_awal.strftime("%Y-%m-%d"))
        elif filter_tanggal_akhir:
            query += " AND tanggal <= ?"
            params.append(filter_tanggal_akhir.strftime("%Y-%m-%d"))

        query += " GROUP BY jenis_aktivitas ORDER BY total_kalori DESC"
        df = database.get_dataframe(query, tuple(params) if params else None)
        if not df.empty:
            df.rename(columns={'jenis_aktivitas': 'Jenis Aktivitas', 'total_kalori': 'Total Kalori Terbakar'}, inplace=True)
        return df

    def get_jumlah_entri_per_kategori(self, tabel_nama: str, tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = f"SELECT COUNT(*) as jumlah FROM {tabel_nama}"
        params = None
        if tanggal:
            query += " WHERE tanggal = ?"
            params = (tanggal.strftime("%Y-%m-%d"),)
        df = database.get_dataframe(query, params)
        return df.iloc[0]['jumlah'] if not df.empty else 0