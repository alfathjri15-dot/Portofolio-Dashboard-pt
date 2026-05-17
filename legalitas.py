import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Custom CSS Dashboard Mewah
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .legal-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .caption-style {
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.85rem;
    }
    h1, h2, h3 { color: #00f2fe !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Membaca Data Standar (Karena CSV Sudah Bersih)
@st.cache_data
def load_legal_data():
    try:
        # Membaca file dengan encoding utf-8-sig untuk membersihkan sisa biner pembuka
        df = pd.read_csv("Data/Legalitas.csv", sep=";", encoding="utf-8-sig")
        # Menghilangkan spasi tak terlihat di nama kolom
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

legal = load_legal_data()

# 3. Fungsi Logika Status
def get_status(tgl_berlaku):
    if pd.isna(tgl_berlaku) or str(tgl_berlaku).strip() in ["—", "", "-", "NaN", "nan"]:
        return "✅ Permanent"
    try:
        today = datetime.now()
        tgl = pd.to_datetime(str(tgl_berlaku).strip(), errors='coerce')
        if pd.isna(tgl):
            return "✅ Permanent"
        return "❌ Expired" if tgl < today else "🟢 Active"
    except:
        return "✅ Permanent"

# Inisialisasi Session State
if "filter_jenis" not in st.session_state:
    st.session_state["filter_jenis"] = "All"
if "search_bar" not in st.session_state:
    st.session_state["search_bar"] = ""

# Layout Atas
col_title, col_search, col_filter = st.columns([5, 1.5, 1.5])

with col_title:
    st.markdown("<h2 style='margin:0;'>⚖️ Company Legality</h2>", unsafe_allow_html=True)

with col_filter:
    with st.popover("⚙️ Filters By", use_container_width=True):
        list_jenis = sorted(legal['Jenis'].dropna().unique().tolist()) if not legal.empty else []
        st.selectbox("Document Type", ["All"] + list_jenis, key="filter_jenis")
        if st.button("Clear Filter", type="primary", use_container_width=True):
            st.session_state["filter_jenis"] = "All"
            st.rerun()

with col_search:
    with st.popover("🔍 Search", use_container_width=True):
        st.text_input("Keywords", placeholder="Type keywords...", key="search_bar")
        if st.button("Clear Search", type="primary", use_container_width=True):
            st.session_state["search_bar"] = ""
            st.rerun()

# Filter Logic
if not legal.empty:
    legal_display = legal.copy()

    if st.session_state["filter_jenis"] != "All":
        legal_display = legal_display[legal_display['Jenis'] == st.session_state["filter_jenis"]]

    if st.session_state["search_bar"]:
        query = st.session_state["search_bar"]
        legal_display = legal_display[
            legal_display.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)
        ]

    st.write(f"Showing **{len(legal_display)}** Records")
    st.markdown("---")

    # 4. Rendering Card
    for index, row in legal_display.iterrows():
        st.markdown('<div class="legal-card">', unsafe_allow_html=True)
        col_leg, col_date, col_link = st.columns([3.5, 2, 2.5])

        with col_leg:
            st.markdown(f"#### {row.get('Dokumen', '-')}")
            st.markdown(f"<span class='caption-style'>Category: {row.get('Jenis', '-')}</span>", unsafe_allow_html=True)
            st.write("")
            st.write(f"**Document Number:**")
            st.code(f"{row.get('Nomor', '-')}", language="text")
            st.markdown(f"<span class='caption-style'>Issuer: {row.get('Pembuat / Terbit Berkas', '-')}</span>", unsafe_allow_html=True)
        
        with col_date:
            tgl_terbit = row.get('Masa Pembuatan', '-')
            tgl_berakhir = row.get('Masa Berlaku', '-')
            status_label = get_status(tgl_berakhir)
            color = "#28a745" if "Expired" not in status_label else "#dc3545"
            
            st.markdown("📅 **Validity Period**")
            st.markdown(f"<span class='caption-style'>Issued Date:</span><br><b>{tgl_terbit}</b>", unsafe_allow_html=True)
            st.write("")
            
            if "Permanent" in status_label:
                st.markdown(f"<span class='caption-style'>Expiry Date:</span><br><span style='color:#28a745; font-weight:bold;'>✅ Permanent</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='caption-style'>Expiry Date:</span><br><span style='color:{color}; font-weight:bold;'>⌛ {tgl_berakhir}</span>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="margin-top: 15px; padding: 6px; border: 1px solid {color}; border-radius: 6px; text-align: center; background: rgba(255,255,255,0.01);">
                    <span style="color:{color}; font-size: 0.85rem; font-weight: bold;">{status_label}</span>
                </div>
            """, unsafe_allow_html=True)
        
        with col_link:
            st.markdown("📄 **Document Preview**")
            link_doc = str(row.get('Link Dokumen', '')).strip()

            if link_doc and "http" in link_doc:
                embed_url = link_doc.replace('/view?usp=sharing', '/preview').replace('/view?usp=share_link', '/preview').replace('/view', '/preview')
                st.markdown(f'<iframe src="{embed_url}" width="100%" height="160px" style="border:1px solid rgba(255,255,255,0.1); border-radius:5px;"></iframe>', unsafe_allow_html=True)
                st.link_button("Open Full File ↗️", link_doc, use_container_width=True)
            else:
                st.info("Preview not available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Database data berkas legalitas kosong.")