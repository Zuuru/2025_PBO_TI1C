# database.py
import sqlite3
import pandas as pd
from konfigurasi import DB_PATH

def get_db_connection() -> sqlite3.Connection | None:
    """Membuka dan mengembalikan koneksi baru ke database SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row # Akses kolom by name
        return conn
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Koneksi DB gagal: {e}");
        return None

def execute_query(query: str, params: tuple | None = None) -> int | None:
    """Menjalankan query non-SELECT. Mengembalikan lastrowid jika INSERT."""
    conn = get_db_connection()
    if not conn: return None

    last_id = None
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Query gagal: {e} | Query: {query[:100]}");
        conn.rollback()
        return None
    finally:
        if conn: conn.close()

def fetch_query(query: str, params: tuple | None = None, fetch_all: bool = True) -> list | sqlite3.Row | None:
    """Menjalankan query SELECT dan mengembalikan hasil."""
    conn = get_db_connection()
    if not conn: return None

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall() if fetch_all else cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Fetch gagal: {e} | Query: {query[:100]}");
        return None
    finally:
        if conn: conn.close()

def get_dataframe(query: str, params: tuple | None = None) -> pd.DataFrame:
    """Menjalankan query SELECT dan mengembalikan DataFrame Pandas."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()

    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"ERROR [database.py] Gagal baca ke DataFrame: {e} | Query: {query[:100]}");
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def setup_database_initial() -> bool:
    """Memastikan semua tabel ada di database."""
    print(f"Memeriksa/membuat tabel di database (via database.py): {DB_PATH}")
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()

        # Table: pengukuran_tubuh
        sql_create_pengukuran = """
        CREATE TABLE IF NOT EXISTS pengukuran_tubuh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            berat_kg REAL NOT NULL CHECK(berat_kg > 0),
            tinggi_cm REAL NOT NULL CHECK(tinggi_cm > 0)
        );"""
        cursor.execute(sql_create_pengukuran)
        print(" -> Tabel 'pengukuran_tubuh' siap.")

        # Table: aktivitas_fisik
        sql_create_aktivitas = """
        CREATE TABLE IF NOT EXISTS aktivitas_fisik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            jenis_aktivitas TEXT NOT NULL,
            durasi_menit INTEGER NOT NULL CHECK(durasi_menit > 0),
            kalori_terbakar REAL
        );"""
        cursor.execute(sql_create_aktivitas)
        print(" -> Tabel 'aktivitas_fisik' siap.")

        # Table: asupan_makanan
        sql_create_makanan = """
        CREATE TABLE IF NOT EXISTS asupan_makanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            deskripsi_makanan TEXT NOT NULL,
            kalori REAL NOT NULL CHECK(kalori >= 0),
            protein_g REAL,
            karbo_g REAL,
            lemak_g REAL
        );"""
        cursor.execute(sql_create_makanan)
        print(" -> Tabel 'asupan_makanan' siap.")

        # Table: asupan_air
        sql_create_air = """
        CREATE TABLE IF NOT EXISTS asupan_air (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            jumlah_ml INTEGER NOT NULL CHECK(jumlah_ml > 0)
        );"""
        cursor.execute(sql_create_air)
        print(" -> Tabel 'asupan_air' siap.")

        # Table: catatan_harian
        sql_create_catatan = """
        CREATE TABLE IF NOT EXISTS catatan_harian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            suasana_hati_skala INTEGER CHECK(suasana_hati_skala >= 1 AND suasana_hati_skala <= 5),
            tingkat_energi_skala INTEGER CHECK(tingkat_energi_skala >= 1 AND tingkat_energi_skala <= 5),
            catatan_tambahan TEXT
        );"""
        cursor.execute(sql_create_catatan)
        print(" -> Tabel 'catatan_harian' siap.")

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error SQLite saat setup tabel: {e}");
        return False
    finally:
        if conn: conn.close()