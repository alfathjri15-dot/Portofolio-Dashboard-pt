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
def get_posisi_vgd(row):
    leader_kolom = str(row['Pemilik Paket']).upper()
    anggota_kolom = str(row['Anggota Paket KSO']).upper()
    nama_target = "VANGUARD"

    if nama_target in leader_kolom: return "Leader"
    if nama_target in anggota_kolom:
        list_anggota = [a.strip() for a in re.split(r'[\n;]', anggota_kolom) if a.strip()]
        for i, nama in enumerate(list_anggota):
            if nama_target in nama: return f"Anggota {i+1}"
    return "Lainnya"

# Load Data Awal
financial = load_data()

# --- HEADER UI ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>💠 FINANCIAL TRACKING INTELLIGENCE</h1>", unsafe_allow_html=True)
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
df_selection['Posisi'] = df_selection.apply(get_posisi_vgd, axis=1)

# --- ROW 2: TREND & PORSI ---
col_center = st.columns(1)

with col_center[0]:
    with st.container():
        st.markdown("<h3 style='text-align: center; color: #8f94fb; margin-bottom: 20px;'>📊 GROSS VS NET REVENUE TREND</h3>", unsafe_allow_html=True)
    
        # --- LOGIKA DATA ---
        df_base = financial[financial['Tahun Filter'].between(2011, 2022)]
        df_trend = df_base.groupby('Tahun Filter').agg({
            'Nilai Kontrak ( $ )': 'sum',
            'Nilai Kontrak Sesuai Porsi ( % )': 'sum'
        }).reset_index()

        # Label untuk angka di tiap titik
        df_trend['txt_total'] = df_trend['Nilai Kontrak ( $ )'].apply(lambda x: f"$ {x/1e6:.2f}M")
        df_trend['txt_porsi'] = df_trend['Nilai Kontrak Sesuai Porsi ( % )'].apply(lambda x: f"$ {x/1e6:.2f}M")

        import plotly.graph_objects as go
        fig_combined = go.Figure()

        # 1. Layer Gross Value (Angka di ATAS titik)
        fig_combined.add_trace(go.Scatter(
            x=df_trend['Tahun Filter'], 
            y=df_trend['Nilai Kontrak ( $ )'],
            mode='lines+markers+text',
            name='Gross Value',
            text=df_trend['txt_total'],
            textposition="top center",
            line=dict(width=3, color='#00f2fe', shape='spline'),
            fill='tonexty',
            fillcolor='rgba(0, 242, 254, 0.1)',
            marker=dict(size=8, line=dict(width=1, color='white')),
            textfont=dict(color='#00f2fe', size=10)
        ))

        # 2. Layer Net Portion (Angka di BAWAH titik)
        fig_combined.add_trace(go.Scatter(
            x=df_trend['Tahun Filter'], 
            y=df_trend['Nilai Kontrak Sesuai Porsi ( % )'],
            mode='lines+markers+text',
            name='Net Portion',
            text=df_trend['txt_porsi'],
            textposition="bottom center",
            line=dict(width=3, color='#8f94fb', shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(143, 148, 251, 0.2)',
            marker=dict(size=8, line=dict(width=1, color='white')),
            textfont=dict(color='#8f94fb', size=10)
        ))

        # --- STYLING ---
        fig_combined.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            height=450, # Ditambah sedikit tingginya agar teks angka tidak terpotong
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            xaxis=dict(showgrid=False, dtick=1), # dtick=1 agar semua tahun muncul
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(255,255,255,0.05)', 
                showticklabels=False,
                range=[0, df_trend['Nilai Kontrak ( $ )'].max() * 1.2] # Beri ruang di atas untuk label
            )
        )

        st.plotly_chart(fig_combined, use_container_width=True)

# --- ROW 1: METRICS ---
t_rev = float(df_selection['Nilai Kontrak ( $ )'].sum())
t_net = float(df_selection['Nilai Kontrak Sesuai Porsi ( % )'].sum())
t_proj = len(df_selection)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>💰 Total Contract Value</div>
                <div class='metric-value'>${t_rev/1e6:.2f}M</div>
            </div>
        """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>🏢 Portion of Contract (VGD)</div>
                <div class='metric-value'>${t_net/1e6:.2f}M</div>
            </div>
        """, unsafe_allow_html=True)
        
with m3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>📑 Active Projects</div>
            <div class='metric-value'>{t_proj} Tenders</div>
        </div>
    """, unsafe_allow_html=True)

# --- ROW 3: PROJECT VALUE VS CATEGORY AVERAGE (ADDITIONAL CHART) ---
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    with st.container():
        # 1. Ganti Judul Jadi TOTAL VALUE agar mencerminkan angka 15 M tersebut
        st.markdown("<h3 style='text-align: center; color: #8f94fb;'>📊 Total Value vs Role</h3>", unsafe_allow_html=True)
        
        # 2. [KUNCI]: Ganti .mean() menjadi .sum() untuk melihat akumulasi totalnya
        total_role = df_selection.groupby('Posisi')['Nilai Kontrak ( $ )'].sum().reset_index()
        
        # 3. Membuat Bar Chart berdasarkan TOTAL
        fig_total_bar = px.bar(
            total_role, 
            x='Posisi', 
            y='Nilai Kontrak ( $ )', 
            color='Posisi', 
            color_discrete_sequence=px.colors.sequential.Electric
        )

        # 4. Tampilkan label teks angka aslinya
        fig_total_bar.update_traces(
            textposition='outside',      
            cliponaxis=False,            
            textfont=dict(size=12, color='white'),
            # Menggunakan %{y:.2f} agar memunculkan angka desimal murninya dari Sumbu Y
            texttemplate='$ %{y:,.2s}'       
        )
        
        fig_total_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color="white", 
            showlegend=False,
            height=350, 
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="", showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig_total_bar, use_container_width=True)

# --- Perbaikan Row 3: Scatter Plot ---
with col_right:
    # Menggunakan container agar judul dan grafik menyatu dalam satu kotak/card
    with st.container():
        # Judul Rata Tengah dengan Gaya Glowing
        st.markdown("<h3 style='text-align: center; color: #8f94fb;'>🌌 Project Distribution Map</h3>", unsafe_allow_html=True)
        
        # Inisialisasi Scatter Plot
        fig_scat = px.scatter(
            df_selection, 
            x='Porsi Kontrak ( % )', 
            y='Nilai Kontrak ( $ )',
            size='Nilai Kontrak ( $ )', 
            color='Posisi', 
            hover_name='Nama Paket Pekerjaan', 
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel # Warna lembut agar tidak silau
        )

        # Styling Grafik agar Transparan dan Masuk ke dalam Card
        fig_scat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color="white",
            height=350, # Samakan tinggi dengan left (Avg Value) agar sejajar
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                title="Porsi Kontrak (%)", 
                gridcolor='rgba(255,255,255,0.05)',
                zeroline=False
            ),
            yaxis=dict(
                title="Nilai Kontrak ( $ )", 
                gridcolor='rgba(255,255,255,0.05)',
                zeroline=False
            ),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=0.5,
            )
        )
        
        st.plotly_chart(fig_scat, use_container_width=True)

# --- ROW 4: ROLE STATISTICS ---
st.markdown("---")
col_left_2, col_right_2 = st.columns(2)

with col_right_2:
    st.markdown("<h3 style='text-align: center; color: #8f94fb;'>🎯 Average Porsi %</h3>", unsafe_allow_html=True)
    avg_p = df_selection['Porsi Kontrak ( % )'].mean()
    fig_pie = px.pie(values=[avg_p, 100-avg_p], names=['VGD', 'Mitra'], hole=0.7,
                     color_discrete_sequence=['#4e54c8', '#1a1d24'])
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, height=380)
    fig_pie.add_annotation(text=f"{avg_p:.0f}%", x=0.5, y=0.5, font_size=25, showarrow=False, font_color="#00f2fe")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_left_2:
    st.markdown("<h3 style='text-align: center; color: #8f94fb;'>📈 KSO Role Statistics (Frequency)</h3>", unsafe_allow_html=True)
    df_pos = df_selection[df_selection['Posisi'] != "Lainnya"]
    if not df_pos.empty:
        counts = df_pos['Posisi'].value_counts().reset_index()
        counts.columns = ['Peran', 'Jumlah']
        fig_roles = px.bar(counts, x='Peran', y='Jumlah', text='Jumlah', color='Peran',
                           color_discrete_map={"Leader": "#00f2fe", "Anggota 1": "#4e54c8", "Anggota 2": "#8f94fb"})
        fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig_roles, use_container_width=True)