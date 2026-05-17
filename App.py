# 1. KONFIGURASI HALAMAN & TEMA
import streamlit as st

# 1. Atur Konfigurasi Halaman Utama (Wajib di paling atas)
st.set_page_config(
    page_title="PT X Consultant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Definisikan Halaman-Halaman yang Saling Terhubung
# Variabel st.Page akan membaca file python lain dan menjadikannya sebuah halaman objek
halaman_dashboard = st.Page("Dashboard_Tender.py", title="Main Dashboard", icon="📊", default=True)
halaman_financial = st.Page("Financial_Tracking.py", title="Financial Performance", icon="💰")
halaman_tender = st.Page("Tender_Data.py", title="Tender & Winning Analysis", icon="📈")
halaman_legal = st.Page("legalitas.py", title="Company Legalitas", icon="⚖️")

st.sidebar.markdown("---")
st.sidebar.caption(
    "🔒 *Compliance Note: All financial and institutional data have been structuraly anonymized into a "
    "fictional setting to satisfy corporate NDA requirements for portfolio demonstration. "
)

# 3. Gabungkan ke dalam Menu Navigasi Sidebar
# Membaginya berdasarkan kategori (Section)
pg = st.navigation({
    "INTELLIGENCE": [halaman_dashboard, halaman_financial],
    "MANAGEMENT": [halaman_tender, halaman_legal]
})

# 4. Jalankan Navigasi
pg.run()