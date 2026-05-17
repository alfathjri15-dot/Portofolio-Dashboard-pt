import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Custom CSS untuk Tampilan Grafik Card
st.markdown("""
<style>
    /* Kontainer Utama Kartu */
    .metric-card {
        background-color: #161a23; /* Warna card lebih terang sedikit dari background luar */
        border: 1px solid #2d323e; /* Border halus agar kotak terlihat tegas */
        border-radius: 25px;       /* Ujung tumpul yang sangat bulat sesuai gambar */
        padding: 30px;             /* Ruang di dalam kotak */
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4); /* Shadow lembut ke bawah */
        margin-bottom: 15px;
    }

    /* Styling Label (GROSS REVENUE) */
    .metric-label {
        color: #8f94fb;            /* Warna ungu muda/biru sesuai gambar */
        font-size: 16px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }

    /* Styling Nilai Angka (Rp 218.85B) */
    .metric-value {
        color: #ffffff;
        font-size: 36px;           /* Angka besar dan tebal */
        font-weight: 800;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Menciptakan style untuk box agar konsisten dengan kartu sebelumnya */
    .stColumn > div {
        background-color: #161a23;
        border: 1px solid #2d323e;
        border-radius: 25px;
        padding: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# 2. FUNGSI LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("Data/Data_Tender.csv", sep=";")
    cols_to_fix = ['Nilai Kontrak ( $ )', 'Porsi Kontrak ( % )', 'Nilai Kontrak Sesuai Porsi ( % )']
    df['Kontrak Awal'] = pd.to_datetime(df['Kontrak Awal'], dayfirst=True, errors='coerce')
    df['Tahun Filter'] = df['Kontrak Awal'].dt.year.fillna(0).astype(int)
    
    for col in cols_to_fix:
        df[col] = df[col].astype(str).str.replace(r'[^0-9,]', '', regex=True).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# 3. LOGIKA DETEKSI POSISI (Double Check: Pemilik & Anggota)
def get_posisi(row):
    leader_kolom = str(row['Pemilik Paket']).upper()
    anggota_kolom = str(row['Anggota Paket KSO']).upper()
    nama_target = "Vanguard"

    if nama_target in leader_kolom: return "Leader"
    if nama_target in anggota_kolom:
        list_anggota = [a.strip() for a in re.split(r'[\n;]', anggota_kolom) if a.strip()]
        for i, nama in enumerate(list_anggota):
            if nama_target in nama: return f"Anggota {i+1}"
    return "Lainnya"

# Load Data Awal
financial = load_data()

# --- HEADER UI ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>💠 DASHBOARD TENDER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8f94fb; font-size: 16px;'>PT. X CONSULTANT</p>", unsafe_allow_html=True)

# 4. FILTER DALAM POPOVER
with st.popover("⚙️ Control Panel"):
    def reset_filters():
        st.session_state["filter_tahun_kontrak"] = "All"
    
    list_tahun = sorted([t for t in financial['Tahun Filter'].unique() if t != 0], reverse=True)

    # Dropdown
    st.write ("Tahun Kontrak :")
    tahun_pilih = st.selectbox(
        "Tahun Kontrak",
        ["All"] + list_tahun,
        key="filter_tahun_kontrak",
        label_visibility="collapsed"
    )
        
    st.button(
        "Clear All Filters", 
        on_click=reset_filters, 
        use_container_width=True, 
        type="primary"
    )

df_selection = financial if tahun_pilih == "All" else financial[financial['Tahun Filter'] == tahun_pilih]
df_selection['Posisi'] = df_selection.apply(get_posisi, axis=1)

# --- ROW 2: TREND & PORSI ---
st.write("")
col_center = st.columns(1)

with col_center[0]:
    with st.container():
        st.markdown("<h3 style='text-align: center; color: #8f94fb; margin-bottom: 20px;'>📍 TENDER DISTRIBUTION BY LOCATION</h3>", unsafe_allow_html=True)
        
        # LOGIKA BARU: Hitung jumlah tender per Lokasi
        # Kita groupby 'Lokasi' dan hitung kemunculannya
        df_loc = financial.groupby('Lokasi').size().reset_index(name='Jumlah Tender')
        
        # Urutkan dari yang terbanyak agar grafik lebih rapi
        df_loc = df_loc.sort_values('Jumlah Tender', ascending=False)

        # Gunakan Bar Chart karena Lokasi adalah data kategorik (bukan tren waktu)
        fig_bar = px.bar(df_loc, x='Lokasi', y='Jumlah Tender', text='Jumlah Tender')

        fig_bar.update_traces(
            marker_color='#00f2fe',
            marker_line_color='white',
            marker_line_width=1,
            opacity=0.8,
            textposition='outside',
            textfont=dict(color='white', size=12)
        )

        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color="white",
            yaxis=dict(
                title="Banyaknya Tender",
                gridcolor='rgba(255,255,255,0.05)',
                zerolinecolor='rgba(255,255,255,0.1)'
            ),
            xaxis=dict(title="Provinsi/Kabupaten", showgrid=False),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )

        st.plotly_chart(fig_bar, use_container_width=True)

# --- ROW 1: METRICS ---
# --- LOGIKA ANALISIS PATTERN ---

if not df_selection.empty:
    # 1. Menentukan Wilayah Terkuat
    top_region = df_selection['Lokasi'].value_counts().idxmax()
    count_region = df_selection['Lokasi'].value_counts().max()
    
    # 2. Menentukan Partner Strategis (Memisahkan data yang digabung)
    # Kita ambil kolom 'Anggota Paket KSO', pecah berdasarkan baris baru atau spasi
    # Lalu kita bersihkan angka persen dan nama perusahaan sendiri
    all_partners = df_selection['Anggota Paket KSO'].str.cat(sep=' ')
    
    # Membersihkan karakter yang tidak perlu agar murni nama PT
    # Menghapus pola persen seperti ( 30 % ) atau (30%)
    clean_partners = re.sub(r'\(\s*\d+\s*%\s*\)', '', all_partners)
    
    # Memisahkan berdasarkan 'PT.' untuk mendapatkan list perusahaan
    partner_list = [p.strip() for p in clean_partners.split('PT.') if p.strip()]
    partner_list = ['PT. ' + p for p in partner_list] # Mengembalikan text PT.
    
    # Menghapus nama perusahaan sendiri dari list partner (agar tidak jadi top partner diri sendiri)
    my_company = "PT. VANGUARD KONSULTAN ENG"
    partner_list = [p for p in partner_list if my_company not in p]

    if partner_list:
        from collections import Counter
        partner_counts = Counter(partner_list)
        top_partner, count_partner = partner_counts.most_common(1)[0]
    else:
        top_partner, count_partner = "No Partner (Mandiri)", 0
else:
    top_region = top_partner = "N/A"
    count_region = count_partner = 0

# 1. Pastikan baris ini ada untuk membuat kolomnya
m1, m2, m3 = st.columns(3)

# 2. Baru kemudian panggil variabelnya di dalam blok 'with'
with m1:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>📍 Winning Base (Region)</div>
            <div class='metric-value' style='font-size: 1.5rem;'>{top_region}</div>
            <div style='color: #00f2fe; font-size: 0.85rem;'>Dominasi di Wilayah Ini</div>
        </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>🤝 Most Reliable Partner</div>
            <div class='metric-value' style='font-size: 1.1rem; line-height: 1.2;'>{top_partner}</div>
            <div style='color: #8f94fb; font-size: 0.85rem;'>Menang Bersama: <b>{count_partner} Kali</b></div>
        </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>📊 Total Winning Pool</div>
            <div class='metric-value' style='font-size: 1.5rem;'>{len(df_selection)} Projects</div>
            <div style='color: #4CAF50; font-size: 0.85rem;'>Data Berhasil Dimasukkan</div>
        </div>
    """, unsafe_allow_html=True)

# Mapping Koordinat Ibu Kota Provinsi di Indonesia
fiksi_coords = {
    'KUNYAVALL': [-2.5489, 118.0149],
    'AETHELGAR': [-6.2088, 106.8456],
    'ELDORIA HIGHLANDS': [-7.0051, 110.4381],
    'SERPENTINE': [-0.9471, 100.4172],
    'VALORIA REGENCY': [-7.2575, 112.7521],
    'EAST SYLVANIS': [-3.3167, 114.5900],
    'TAPHIN-GARD': [-5.1476, 119.4327],
    'VALYI REGENCY': [-3.9722, 122.5149],
    'VANGUARD': [-5.4500, 105.2667]
}

with st.container():
    st.markdown("<h3 style='text-align: center; color: #8f94fb; margin-bottom: 20px;'>🗺️ GEOSPATIAL WINNING PATTERN</h3>", unsafe_allow_html=True)

    # 1. Hitung jumlah tender per lokasi fiksi
    df_loc = df_selection.groupby('Lokasi').size().reset_index(name='Jumlah Tender')

    # 2. Masukkan koordinat berdasarkan nama lokasi fiksi (bersihkan spasi & jadikan uppercase)
    df_loc['lat'] = df_loc['Lokasi'].apply(lambda x: fiksi_coords.get(str(x).strip().upper(), [None, None])[0])
    df_loc['lon'] = df_loc['Lokasi'].apply(lambda x: fiksi_coords.get(str(x).strip().upper(), [None, None])[1])

    # [PENTING] FILTER JIKA ADA LOKASI YANG KOORDINATNYA TIDAK TERDAFTAR AGAR TIDAK EROR
    df_loc = df_loc.dropna(subset=['lat', 'lon'])

    # 3. Buat Peta Scatter Geo
    fig_map = px.scatter_geo(
        df_loc,
        lat='lat',
        lon='lon',
        size='Jumlah Tender',
        color='Jumlah Tender',
        hover_name='Lokasi',
        text='Jumlah Tender',
        projection="natural earth",
        color_continuous_scale='Viridis'
    )

    # 4. Fokuskan kamera ke area peta Indonesia tempat titik fiksi berada
    fig_map.update_geos(
        visible=False,
        showcountries=True,
        countrycolor="#444",
        showland=True,
        landcolor="rgba(255, 255, 255, 0.05)",
        lataxis_range=[-11, 6],
        lonaxis_range=[95, 141]
    )

    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )

    st.plotly_chart(fig_map, use_container_width=True)

# --- ANALISIS TAMBAHAN: ROLE & SEASONALITY ---
st.markdown("<h3 style='text-align: center; color: #8f94fb; margin-bottom: 25px;'>🔍 IN-DEPTH WINNING PATTERNS</h3>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# --- KOLOM KIRI: ROLE DOMINANCE (LEADER VS MEMBER) ---
with col_left:
    with st.container():
        st.markdown("<h5 style='text-align: center; color: white;'>🏆 Role Dominance</h5>", unsafe_allow_html=True)
        
        my_company = "PT. VANGUARD KONSULTAN ENG"
        # Pastikan kolom 'Leader' ada, sesuaikan jika namanya berbeda di Excel
        df_selection['Role'] = df_selection['Pemilik Paket'].apply(
            lambda x: 'Pemilik Paket' if my_company.upper() in str(x).upper() else 'Member'
        )
        role_counts = df_selection['Role'].value_counts().reset_index(name='Total')

        fig_role = px.pie(
            role_counts, 
            values='Total', 
            names='Role',
            hole=0.6,
            color_discrete_sequence=['#00f2fe', '#8f94fb']
        )
        
        fig_role.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color="white"), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        
        st.plotly_chart(fig_role, use_container_width=True)

# --- KOLOM KANAN: WINNING SEASONALITY (BY MONTH) ---
with col_right:
    with st.container():
        st.markdown("<h5 style='text-align: center; color: white;'>📅 Winning Seasonality</h5>", unsafe_allow_html=True)
        
        # Ekstrak bulan dari kolom Tanggal/Kontrak (asumsi sudah tipe datetime)
        # Jika belum datetime, gunakan: df_selection['Bulan'] = pd.to_datetime(df_selection['Tanggal']).dt.month_name()
        df_selection['Bulan'] = df_selection['Kontrak Awal'].dt.month_name()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        df_month = df_selection.groupby('Bulan').size().reset_index(name='Jumlah')
        
        # Urutkan berdasarkan urutan kalender
        df_month['Bulan'] = pd.Categorical(df_month['Bulan'], categories=month_order, ordered=True)
        df_month = df_month.sort_values('Bulan')

        fig_month = px.bar(
            df_month,
            x='Bulan',
            y='Jumlah',
            text='Jumlah'
        )

        fig_month.update_traces(
            marker_color='#00f2fe',
            textposition='outside',
            textfont=dict(color='white')
        )

        fig_month.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="Tender Won", showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            margin=dict(t=20, b=0, l=0, r=0),
            height=300
        )

        st.plotly_chart(fig_month, use_container_width=True)

def shorten_owner_name(name):
    # Menghapus detail SNVT/Pelaksanaan agar murni nama Balai-nya
    if 'SNVT' in name:
        name = name.split('SNVT')[0].strip()
    
    # Mengubah "BALAI BESAR WILAYAH SUNGAI" menjadi "BBWS"
    name = name.replace("BALAI BESAR WILAYAH SUNGAI", "BBWS")
    name = name.replace("BALAI WILAYAH SUNGAI", "BWS")
    
    # Batasi jumlah karakter agar tidak terlalu panjang di grafik
    return name[:30] + '...' if len(name) > 30 else name

col_center_1 = st.columns(1)

with col_center_1[0]:
    with st.container():
        # Gunakan margin-top agar ada jarak dari elemen di atasnya
        st.markdown("<h3 style='text-align: center; color: #8f94fb; margin-top: 30px;'>🏛️ OWNER & CLIENT DOMINANCE</h3>", unsafe_allow_html=True)
    
        if not df_selection.empty:
            # 1. Menghitung jumlah tender
            df_owner = df_selection.groupby('Nama').size().reset_index(name='Jumlah')
        
            # [NEW] Menyingkat Nama Instansi agar tidak penuh di kiri
            df_owner['Sumbbu Y'] = df_owner['Nama'].apply(shorten_owner_name)
        
            # Ambil Top 8 agar tidak terlalu padat
            df_owner = df_owner.sort_values('Jumlah', ascending=True).tail(8) 

            # 2. Membuat Grafik (Hapus parameter color agar tidak belang)
            fig_owner = px.bar(
                df_owner,
                y='Sumbbu Y', # Gunakan nama yang disingkat
                x='Jumlah',
                orientation='h',
                text='Jumlah', # Tampilkan angka di ujung batang
                # Hapus parameter color='Jumlah' di sini
            )

            # 3. Styling Total (Glow & High Contrast)
            fig_owner.update_traces(
                # Gunakan SATU WARNA dominan (Cyan bersinar) untuk semua batang
                marker_color='rgba(0, 242, 254, 0.7)',
                marker_line_color='white',
                marker_line_width=0.8,
            
                # Memperbaiki Teks Angka
                textposition='outside', # Pastikan angka selalu di luar
                textfont=dict(color='white', size=12), # Teks putih yang high contrast
                opacity=0.9
            )

            fig_owner.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white"),
            
                # Memperbaiki Grid
                xaxis=dict(
                    showgrid=True,
                    visible=False, # Sembunyikan sumbu X karena angka sudah ada di batang
                    gridcolor='rgba(255, 255, 255, 0.05)'
                ),
                yaxis=dict(
                    title="", 
                    showgrid=False,
                    # Pastikan teks label sumbu Y tidak terpotong
                    tickfont=dict(size=10, color="rgba(255,255,255,0.7)") 
                ),
            
                margin=dict(l=10, r=30, t=10, b=10), # Sesuaikan margin kiri-kanan
                height=350, # Kurangi sedikit tinggi agar lebih kompak
            )

            st.plotly_chart(fig_owner, use_container_width=True)
        else:
            st.info("Pilih filter terlebih dahulu.")