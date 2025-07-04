# streamlit_app.py
import streamlit as st
import datetime
import pandas as pd
import locale
import calendar # For week number in trends

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        print("Locale id_ID/Indonesian tidak tersedia.")

def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp')[:-3] # Remove .00
    except:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")

# Import modules
try:
    from model import PengukuranTubuh, AktivitasFisik, AsupanMakanan, AsupanAir, CatatanHarian
    from manajer_wellness import WellnessTracker
    from konfigurasi import KATEGORI_AKTIVITAS, SKALA_SUASANA_ENERGI
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada di direktori yang sama.")
    st.stop()

st.set_page_config(page_title="Personal Wellness Tracker", layout="wide", initial_sidebar_state="expanded")

# Initialize Wellness Manager (Use Cache)
@st.cache_resource
def get_wellness_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi WellnessTracker...")
    return WellnessTracker() # Ini akan memicu cek DB/Tabel di init

wellness_manager = get_wellness_manager()

# --- Fungsi Halaman/UI ---

def halaman_dashboard():
    st.header("✨ Dashboard Harian")

    today = datetime.date.today()
    st.subheader(f"Ringkasan Hari Ini ({today.strftime('%d %B %Y')})")

    col1, col2, col3, col4 = st.columns(4)

    # Kalori
    total_kalori_makanan, total_kalori_terbakar = wellness_manager.hitung_total_kalori_harian(today)
    col1.metric(label="Kalori Masuk (makanan)", value=f"{total_kalori_makanan:,.0f} Kkal")
    col2.metric(label="Kalori Keluar (aktivitas)", value=f"{total_kalori_terbakar:,.0f} Kkal")

    # Air
    total_air = wellness_manager.hitung_total_air_harian(today)
    col3.metric(label="Asupan Air", value=f"{total_air:,.0f} ml")

    # IMT
    latest_imt_data = wellness_manager.get_latest_imt()
    if latest_imt_data and latest_imt_data[1] == today:
        imt_val, imt_date = latest_imt_data
        col4.metric(label="IMT Terbaru", value=f"{imt_val:.2f}")
    else:
        col4.metric(label="IMT Terbaru", value="N/A", help="Belum ada data pengukuran tubuh hari ini.")

    st.divider()
    st.subheader("Detail Hari Ini")

    # Makanan Hari Ini
    st.write("#### Asupan Makanan Hari Ini")
    df_makanan_hari_ini = wellness_manager.get_riwayat_makanan(today)
    if not df_makanan_hari_ini.empty:
        st.dataframe(df_makanan_hari_ini.drop(columns=['id', 'Tanggal']), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada asupan makanan hari ini.")

    # Aktivitas Hari Ini
    st.write("#### Aktivitas Fisik Hari Ini")
    df_aktivitas_hari_ini = wellness_manager.get_riwayat_aktivitas(today)
    if not df_aktivitas_hari_ini.empty:
        st.dataframe(df_aktivitas_hari_ini.drop(columns=['id', 'Tanggal']), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada aktivitas fisik hari ini.")

    # Catatan Harian Hari Ini
    st.write("#### Catatan Harian Hari Ini")
    df_catatan_hari_ini = wellness_manager.get_riwayat_catatan(today)
    if not df_catatan_hari_ini.empty:
        st.dataframe(df_catatan_hari_ini.drop(columns=['id', 'Tanggal']), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada catatan harian hari ini.")


def halaman_input_data_baru():
    st.header("📝 Input Data Baru")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pengukuran Tubuh", "Aktivitas Fisik", "Asupan Makanan", "Asupan Air", "Catatan Harian"])

    with tab1:
        st.subheader("Tambah Pengukuran Tubuh")
        with st.form("form_pengukuran_tubuh", clear_on_submit=True):
            tgl_ukur = st.date_input("Tanggal Pengukuran*", value=datetime.date.today())
            col_b, col_t = st.columns(2)
            berat_kg = col_b.number_input("Berat Badan (kg)*:", min_value=0.1, max_value=500.0, step=0.1, format="%.1f")
            tinggi_cm = col_t.number_input("Tinggi Badan (cm)*:", min_value=0.1, max_value=300.0, step=0.1, format="%.1f")
            submitted_ukur = st.form_submit_button("Simpan Pengukuran")
            if submitted_ukur:
                if berat_kg <= 0 or tinggi_cm <= 0:
                    st.warning("Berat dan Tinggi badan harus positif!", icon="⚠️")
                else:
                    with st.spinner("Menyimpan..."):
                        pengukuran_baru = PengukuranTubuh(tgl_ukur, berat_kg, tinggi_cm)
                        if wellness_manager.tambah_pengukuran(pengukuran_baru):
                            st.success("Pengukuran tubuh berhasil disimpan!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan pengukuran tubuh.", icon="❌")

    with tab2:
        st.subheader("Tambah Aktivitas Fisik")
        with st.form("form_aktivitas_fisik", clear_on_submit=True):
            tgl_aktivitas = st.date_input("Tanggal Aktivitas*", value=datetime.date.today())
            jenis_aktivitas = st.selectbox("Jenis Aktivitas*:", KATEGORI_AKTIVITAS)
            durasi_menit = st.number_input("Durasi (menit)*:", min_value=1, step=5)
            kalori_terbakar = st.number_input("Kalori Terbakar (perkiraan):", min_value=0.0, step=10.0, format="%.0f", help="Kosongkan jika tidak tahu.")
            submitted_aktivitas = st.form_submit_button("Simpan Aktivitas")
            if submitted_aktivitas:
                if durasi_menit <= 0:
                    st.warning("Durasi aktivitas harus positif!", icon="⚠️")
                else:
                    with st.spinner("Menyimpan..."):
                        aktivitas_baru = AktivitasFisik(tgl_aktivitas, jenis_aktivitas, durasi_menit, kalori_terbakar if kalori_terbakar > 0 else None)
                        if wellness_manager.tambah_aktivitas(aktivitas_baru):
                            st.success("Aktivitas fisik berhasil disimpan!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan aktivitas fisik.", icon="❌")

    with tab3:
        st.subheader("Tambah Asupan Makanan")
        with st.form("form_asupan_makanan", clear_on_submit=True):
            tgl_makan = st.date_input("Tanggal Asupan*", value=datetime.date.today())
            deskripsi_makanan = st.text_input("Deskripsi Makanan*:", placeholder="Contoh: Nasi Goreng, Dada Ayam")
            kalori_makan = st.number_input("Kalori (Kkal)*:", min_value=0.0, step=10.0, format="%.0f")
            col_p, col_k, col_l = st.columns(3)
            protein_g = col_p.number_input("Protein (g):", min_value=0.0, step=0.1, format="%.1f")
            karbo_g = col_k.number_input("Karbohidrat (g):", min_value=0.0, step=0.1, format="%.1f")
            lemak_g = col_l.number_input("Lemak (g):", min_value=0.0, step=0.1, format="%.1f")
            submitted_makanan = st.form_submit_button("Simpan Asupan Makanan")
            if submitted_makanan:
                if not deskripsi_makanan or kalori_makan < 0:
                    st.warning("Deskripsi dan Kalori wajib diisi!", icon="⚠️")
                else:
                    with st.spinner("Menyimpan..."):
                        makanan_baru = AsupanMakanan(tgl_makan, deskripsi_makanan, kalori_makan, protein_g, karbo_g, lemak_g)
                        if wellness_manager.tambah_makanan(makanan_baru):
                            st.success("Asupan makanan berhasil disimpan!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan asupan makanan.", icon="❌")

    with tab4:
        st.subheader("Tambah Asupan Air")
        with st.form("form_asupan_air", clear_on_submit=True):
            tgl_air = st.date_input("Tanggal Asupan Air*", value=datetime.date.today())
            jumlah_ml = st.number_input("Jumlah Air (ml)*:", min_value=1, step=100)
            submitted_air = st.form_submit_button("Simpan Asupan Air")
            if submitted_air:
                if jumlah_ml <= 0:
                    st.warning("Jumlah air harus positif!", icon="⚠️")
                else:
                    with st.spinner("Menyimpan..."):
                        air_baru = AsupanAir(tgl_air, jumlah_ml)
                        if wellness_manager.tambah_air(air_baru):
                            st.success("Asupan air berhasil disimpan!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan asupan air.", icon="❌")

    with tab5:
        st.subheader("Tambah Catatan Harian")
        with st.form("form_catatan_harian", clear_on_submit=True):
            tgl_catatan = st.date_input("Tanggal Catatan*", value=datetime.date.today())
            col_sh, col_te = st.columns(2)
            suasana_hati = col_sh.selectbox("Skala Suasana Hati (1=Buruk, 5=Baik):", [None] + SKALA_SUASANA_ENERGI, format_func=lambda x: "Pilih" if x is None else str(x))
            tingkat_energi = col_te.selectbox("Skala Tingkat Energi (1=Rendah, 5=Tinggi):", [None] + SKALA_SUASANA_ENERGI, format_func=lambda x: "Pilih" if x is None else str(x))
            catatan_tambahan = st.text_area("Catatan Tambahan:")
            submitted_catatan = st.form_submit_button("Simpan Catatan Harian")
            if submitted_catatan:
                if suasana_hati is None and tingkat_energi is None and not catatan_tambahan:
                    st.warning("Minimal isi salah satu (skala atau catatan)!", icon="⚠️")
                else:
                    with st.spinner("Menyimpan..."):
                        catatan_baru = CatatanHarian(tgl_catatan, suasana_hati, tingkat_energi, catatan_tambahan)
                        if wellness_manager.tambah_catatan(catatan_baru):
                            st.success("Catatan harian berhasil disimpan!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan catatan harian.", icon="❌")

def halaman_riwayat_analisis():
    st.header("📚 Riwayat & Analisis Data")

    # Filter Periode
    st.subheader("Filter Data")
    col_filter1, col_filter2 = st.columns(2)
    periode_filter_option = col_filter1.selectbox(
        "Pilih Periode:",
        ["Semua Waktu", "Hari Ini", "Minggu Ini", "Bulan Ini", "Pilih Rentang Tanggal"],
        key="periode_filter"
    )

    start_date, end_date = None, None
    if periode_filter_option == "Hari Ini":
        start_date = datetime.date.today()
        end_date = datetime.date.today()
    elif periode_filter_option == "Minggu Ini":
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=today.weekday()) # Monday
        end_date = start_date + datetime.timedelta(days=6) # Sunday
    elif periode_filter_option == "Bulan Ini":
        today = datetime.date.today()
        start_date = today.replace(day=1)
        end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif periode_filter_option == "Pilih Rentang Tanggal":
        start_date = col_filter2.date_input("Tanggal Mulai:", value=datetime.date.today() - datetime.timedelta(days=7))
        end_date = col_filter2.date_input("Tanggal Akhir:", value=datetime.date.today())

    st.divider()

    # --- Riwayat Data ---
    st.subheader("Riwayat Data Detail")
    tab_riwayat1, tab_riwayat2, tab_riwayat3, tab_riwayat4, tab_riwayat5 = st.tabs([
        "Pengukuran Tubuh", "Aktivitas Fisik", "Asupan Makanan", "Asupan Air", "Catatan Harian"
    ])

    def display_and_delete(df: pd.DataFrame, delete_func, data_type: str):
        if df.empty:
            st.info(f"Belum ada data {data_type} untuk periode ini.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.write(f"Hapus {data_type}:")
            col_id, col_btn = st.columns([0.7, 0.3])
            id_to_delete = col_id.number_input(f"Masukkan ID {data_type} yang akan dihapus:", min_value=1, value=1, key=f"delete_{data_type}_id")
            if col_btn.button(f"Hapus {data_type} Terpilih", key=f"delete_{data_type}_btn"):
                if st.session_state.get(f'confirm_delete_{data_type}_{id_to_delete}', False):
                    with st.spinner("Menghapus..."):
                        if delete_func(id_to_delete):
                            st.success(f"Data {data_type} (ID: {id_to_delete}) berhasil dihapus!", icon="✅")
                            st.cache_data.clear()
                            st.session_state[f'confirm_delete_{data_type}_{id_to_delete}'] = False # Reset confirmation
                            st.rerun()
                        else:
                            st.error(f"Gagal menghapus data {data_type} (ID: {id_to_delete}). Pastikan ID benar.", icon="❌")
                else:
                    st.session_state[f'confirm_delete_{data_type}_{id_to_delete}'] = True
                    st.warning(f"Apakah Anda yakin ingin menghapus data {data_type} dengan ID: {id_to_delete}? Klik 'Hapus {data_type} Terpilih' lagi untuk konfirmasi.", icon="⚠️")


    with tab_riwayat1:
        st.subheader("Riwayat Pengukuran Tubuh")
        with st.spinner("Memuat riwayat pengukuran..."):
            df_ukur = wellness_manager.get_riwayat_pengukuran(start_date if start_date == end_date else None) if periode_filter_option != "Semua Waktu" else wellness_manager.get_riwayat_pengukuran()
            display_and_delete(df_ukur, wellness_manager.hapus_pengukuran, "Pengukuran Tubuh")

    with tab_riwayat2:
        st.subheader("Riwayat Aktivitas Fisik")
        with st.spinner("Memuat riwayat aktivitas..."):
            df_aktivitas = wellness_manager.get_riwayat_aktivitas(start_date if start_date == end_date else None) if periode_filter_option != "Semua Waktu" else wellness_manager.get_riwayat_aktivitas()
            display_and_delete(df_aktivitas, wellness_manager.hapus_aktivitas, "Aktivitas Fisik")

    with tab_riwayat3:
        st.subheader("Riwayat Asupan Makanan")
        with st.spinner("Memuat riwayat makanan..."):
            df_makanan = wellness_manager.get_riwayat_makanan(start_date if start_date == end_date else None) if periode_filter_option != "Semua Waktu" else wellness_manager.get_riwayat_makanan()
            display_and_delete(df_makanan, wellness_manager.hapus_makanan, "Asupan Makanan")

    with tab_riwayat4:
        st.subheader("Riwayat Asupan Air")
        with st.spinner("Memuat riwayat air..."):
            df_air = wellness_manager.get_riwayat_air(start_date if start_date == end_date else None) if periode_filter_option != "Semua Waktu" else wellness_manager.get_riwayat_air()
            display_and_delete(df_air, wellness_manager.hapus_air, "Asupan Air")

    with tab_riwayat5:
        st.subheader("Riwayat Catatan Harian")
        with st.spinner("Memuat riwayat catatan..."):
            df_catatan = wellness_manager.get_riwayat_catatan(start_date if start_date == end_date else None) if periode_filter_option != "Semua Waktu" else wellness_manager.get_riwayat_catatan()
            display_and_delete(df_catatan, wellness_manager.hapus_catatan, "Catatan Harian")

    st.divider()

    # --- Analisis Data ---
    st.subheader("Analisis Tren dan Ringkasan")

    tab_analisis1, tab_analisis2 = st.tabs(["Tren Berat Badan & IMT", "Kalori & Makro Nutrisi"])

    with tab_analisis1:
        st.write("#### Tren Berat Badan")
        periode_tren = st.selectbox("Periode Tren Berat Badan:", ["harian", "mingguan", "bulanan"])
        with st.spinner("Memuat data tren berat badan..."):
            df_tren_berat = wellness_manager.get_data_tren_berat_badan(periode_tren)
            if not df_tren_berat.empty:
                st.line_chart(df_tren_berat.set_index('periode'))
            else:
                st.info("Belum ada data pengukuran tubuh untuk menampilkan tren.")

        st.write("#### Tren IMT (Indeks Massa Tubuh)")
        with st.spinner("Memuat data tren IMT..."):
            df_imt = wellness_manager.get_riwayat_pengukuran() # Get all for IMT trend
            if not df_imt.empty:
                df_imt['Tanggal'] = pd.to_datetime(df_imt['Tanggal'])
                df_imt = df_imt.sort_values(by='Tanggal')
                df_imt['IMT'] = pd.to_numeric(df_imt['IMT'])
                st.line_chart(df_imt.set_index('Tanggal')['IMT'])
            else:
                st.info("Belum ada data pengukuran tubuh untuk menampilkan tren IMT.")


    with tab_analisis2:
        st.write("#### Total Kalori Makanan vs. Kalori Terbakar")
        kalori_start_date = st.date_input("Tanggal Mulai Kalori:", value=datetime.date.today() - datetime.timedelta(days=7), key="kalori_start")
        kalori_end_date = st.date_input("Tanggal Akhir Kalori:", value=datetime.date.today(), key="kalori_end")

        if kalori_start_date > kalori_end_date:
            st.warning("Tanggal mulai tidak boleh lebih dari tanggal akhir.", icon="⚠️")
        else:
            dates = [kalori_start_date + datetime.timedelta(days=x) for x in range((kalori_end_date - kalori_start_date).days + 1)]
            data_kalori = []
            for dt in dates:
                total_makan, total_terbakar = wellness_manager.hitung_total_kalori_harian(dt)
                data_kalori.append({
                    'Tanggal': dt.strftime('%Y-%m-%d'),
                    'Kalori Masuk': total_makan,
                    'Kalori Keluar': total_terbakar
                })
            df_kalori = pd.DataFrame(data_kalori).set_index('Tanggal')
            if not df_kalori.empty:
                st.bar_chart(df_kalori)
            else:
                st.info("Tidak ada data kalori untuk rentang tanggal ini.")

        st.write("#### Ringkasan Makronutrisi Harian")
        makro_date = st.date_input("Pilih Tanggal untuk Ringkasan Makro:", value=datetime.date.today(), key="makro_date")
        makro_data = wellness_manager.get_ringkasan_makro(makro_date)
        if makro_data:
            df_makro = pd.DataFrame([makro_data]).T
            df_makro.columns = ['Jumlah (g)']
            st.dataframe(df_makro.style.format("{:.1f}"), use_container_width=True)
            st.bar_chart(df_makro)
        else:
            st.info("Tidak ada data makronutrisi untuk tanggal ini.")

        st.write("#### Kalori Terbakar per Jenis Aktivitas")
        aktivitas_start_date = st.date_input("Tanggal Mulai Aktivitas:", value=datetime.date.today() - datetime.timedelta(days=30), key="aktivitas_start")
        aktivitas_end_date = st.date_input("Tanggal Akhir Aktivitas:", value=datetime.date.today(), key="aktivitas_end")
        if aktivitas_start_date > aktivitas_end_date:
            st.warning("Tanggal mulai tidak boleh lebih dari tanggal akhir.", icon="⚠️")
        else:
            df_kalori_aktivitas = wellness_manager.get_kalori_aktivitas_per_jenis(aktivitas_start_date, aktivitas_end_date)
            if not df_kalori_aktivitas.empty:
                st.bar_chart(df_kalori_aktivitas.set_index('Jenis Aktivitas'))
            else:
                st.info("Tidak ada data kalori terbakar per jenis aktivitas untuk rentang tanggal ini.")


def main():
    st.sidebar.title("🩺 Personal Wellness Tracker")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Dashboard Harian", "Input Data Baru", "Riwayat & Analisis"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi Pelacak Kesehatan dan Kebugaran Komprehensif")

    # The manager is already initialized via @st.cache_resource at the top level
    # wellness_manager = get_wellness_manager() # No need to call here again

    if menu_pilihan == "Dashboard Harian":
        halaman_dashboard()
    elif menu_pilihan == "Input Data Baru":
        halaman_input_data_baru()
    elif menu_pilihan == "Riwayat & Analisis":
        halaman_riwayat_analisis()

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")

if __name__ == "__main__":
    main()