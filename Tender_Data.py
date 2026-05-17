import streamlit as st
import pandas as pd
import re


# Custom CSS untuk tampilan Dashboard (Glassmorphism)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Efek Kartu Glassmorphism */
    .metric-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    
    .metric-label { color: #8f94fb; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { color: #ffffff; font-size: 28px; font-weight: bold; margin-top: 5px; }

    /* Header Styling */
    h1, h2, h3 { color: #00f2fe !important; }
    </style>
    """, unsafe_allow_html=True)



st.markdown("<h1 style='text-align: center;'>Tender </h1>", unsafe_allow_html=True)

# 1. Membaca Data Dari CSV
try:
    data = pd.read_csv("Data/Data_Tender.csv", sep=";")

    # KONVERSI TANGGAL - Mengubah Kolom menjadi Format Tanggal (datetime)
    data['Kontrak Awal'] = pd.to_datetime(data['Kontrak Awal'], dayfirst=True, errors='coerce')

    # Membuat Kolom baru 'Tahun' untuk keperluan filter
    data['Tahun Filter'] = data['Kontrak Awal'].dt.year.fillna(0).astype(int)

except Exception as e:
    st.error(f"Gagal memuat data {e}")

# 2. Filter & Search
col_title, col_empty, col_search, col_filter = st.columns([4, 2, 1, 1])

with col_title:
    st.subheader("Data")

with col_filter:
    # Menggunakan Popover untuk menyembunyikan filter
    with st.popover("⚙️ Filters By"):
        def reset_filters():
            st.session_state["filter_tahun_kontrak"] = "All"
            st.session_state["filter_wilayah"] = "All"

        st.markdown("### Filter Options")

        #Ambil list unik
        list_tahun = sorted([t for t in data['Tahun Filter'].unique() if t !=0], reverse=True)
        list_wilayah = sorted(data['Lokasi'].unique().tolist())

        # Dropdown
        st.write ("Tahun Kontrak :")
        tahun_pilih = st.selectbox(
            "Tahun Kontrak",
            ["All"] + list_tahun,
            key="filter_tahun_kontrak",
            label_visibility="collapsed"
        )

        st.write("Wilayah : ")
        wilayah_pilih = st.selectbox(
            "Wilayah",
            ["All"] + list_wilayah,
            key="filter_wilayah",
            label_visibility="collapsed"
        )

        st.button(
            "Clear All Filters", 
            on_click=reset_filters, 
            use_container_width=True, 
            type="primary"
        )

        # Fungsi untuk mengosongkan semua filter

    

# Logika Filtering
with col_search:
    with st.popover("🔍 Search"):
        def reset_filters():
            st.session_state["search_bar"] = ""

        st.markdown("### Search Data")
        search_query = st.text_input(
            "Cari", 
            placeholder="Ketik kata kunci...", 
            key="search_bar",
            label_visibility="collapsed"
        )

        st.button(
            "Clear All Search", 
            on_click=reset_filters, 
            use_container_width=True, 
            type="primary",
            key="clear_search_btn"
        )

# Logika Filtering
data_display = data.copy()

if tahun_pilih != "All":
    data_display = data_display[data_display['Tahun Filter'] == tahun_pilih]

if wilayah_pilih != "All":
    data_display = data_display[data_display['Lokasi'] == wilayah_pilih]

if search_query:
    data_display = data_display[data_display.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]


# 3. Filter Text
# Tentukan bagian teks filter secara dinamis
filter_text = ""

if tahun_pilih != "All" and wilayah_pilih != "All":
    filter_text = f"di **{wilayah_pilih}** pada tahun **{tahun_pilih}**"
elif tahun_pilih != "All":
    filter_text = f"pada tahun **{tahun_pilih}**"
elif wilayah_pilih != "All":
    filter_text = f"di **{wilayah_pilih}**"
else:
    filter_text = "Keseluruhan"

#Tampilkan pesan ringkasan
st.write(f"Menampilkan **{len(data_display)}** Proyek ({filter_text})")

# 4. Tender Data Card
for index, row in data_display.iterrows():
    with st.container(border=True):
        # Membagi menjadi 6 kolom dengan rasio lebar yang disesuaikan
        col_sub, col_date, col_member, col_class, col_cost, col_doc = st.columns([3, 1.2, 1.5, 1.2, 1.2, 1.2])

        # Judul Tender (Paling kiri)
        with col_sub:
            st.markdown(f"### {row.get('Nama Paket Pekerjaan', '-')}")
            st.caption(f"📍 {row.get('Lokasi', '-')}")
            st.caption(f"👤 {row.get('Nama', '-')}")
            st.caption(f"📄 {row.get('Nomor / Tanggal', '-')}")
        
        # Tanggal
        with col_date:
            tgl_awal = row.get('Kontrak Awal')
            tgl_akhir = row.get('Kontrak Berakhir')
            tgl_bast = row.get('BAST')

            # Kontrak Awal
            st.write("📅 **Kontrak**")
            st.caption("Awal:")
            st.write(tgl_awal.strftime('%A, %d %b %Y') if pd.notna(tgl_awal) else "-")

            # Perjanjian Kontrak Selesai
            st.caption("Akhir:")
            st.write(tgl_akhir if pd.isna(tgl_akhir) else tgl_akhir)

            # Serah Terima
            st.caption("BAST:")
            st.write(tgl_bast if pd.isna(tgl_bast) else tgl_bast)
        
        #Anggota KSO
        with col_member:
            lead = row.get('Pemilik Paket', '-')
            anggota = row.get('Anggota Paket KSO', '-')

            st.write("🤝 **Keanggotaan**")
    
            # Menampilkan Leader
            st.caption("Leader:")
            st.write(f"🏆 {lead}")

            # Menampilkan Anggota
            st.caption("Anggota KSO:")

            #re.sub akan mencari tanda ')' dan spasi setelahnya
            #lalu menggnatinya dengan ')' + baris baru
            if anggota and anggota != '-':
                anggota_rapi = re.sub(r'\)s+', ') \n', anggota)
                st.text(anggota_rapi)
            else:
                st.write("-")
        
        # Subklasifikasi
        with col_class:
            st.write("🏛️ **Subklasifikasi**")
            subklas = row.get('Bidang / Sub Bidang / Layanan')
            kbli_17 = row.get('KBLI 2015/2017')
            kbli_20 = row.get('KBLI 2020')

            # Klass
            st.caption("Bidang / Sub Bidang: ")
            st.write(f"{subklas}")

            # KLBI
            st.caption("KLBI 2015 / 2017:")
            st.write(f"{kbli_17}")

            st.caption("KLBI 2020:")
            st.write(f"{kbli_20}")
        
        # Nominal Tender
        with col_cost:
            st.write("💰 **Nominal Tender**")
            porsi = row.get('Nilai Kontrak ( Rp. )')
            presentase = row.get('Porsi Kontrak ( % )')
            porsi_kontrak = row.get('Nilai Kontrak Sesuai Porsi ( % )')

            # Kontrak Tender
            st.caption("Nilai Kontrak:")
            st.write(f"{porsi}")

            # Porsi PT
            st.caption("Porsi Kontrak:")
            st.write(f"{presentase}")

            # Kontrak PT
            st.caption("Nilai Kontrak Sesuai Porsi:")
            st.write(f"{porsi_kontrak}")
        
        # Dokumen
        with col_doc:
            st.write("📃 **Dokumen Kelengkapan**")
            # Ganti 'Nominal Porsi' sesuai nama kolom di CSV-mu

            list_dok = ["Surat Perjanjian", "Surat KSO", "BAST", "Adendum", "RAB"]
    
            for i, dok in enumerate(list_dok):
                status = row.get(dok)

                if status in [True, 1, "True", "1"]:
                    st.markdown(f"✅ **{dok}**")
                else:
                    st.markdown(f"❌ <span style='color: gray;'>{dok}</span>", unsafe_allow_html=True)
