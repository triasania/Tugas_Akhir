import streamlit as st
import pandas as pd
import base64
from sistem_rekomendasi_buat_sidang import load_system, get_recommendations

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Rekomendasi Mata Kuliah ITB", page_icon="🐘", layout="wide")

# Fungsi Background & Glassmorphism
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Tema Terang (Default) */
        .block-container {{
            background: rgba(255, 255, 255, 0.75);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.03);
            margin-top: 2rem;
            margin-bottom: 6rem;
        }}

        /* Tema Gelap (Night Mode) */
        @media (prefers-color-scheme: dark) {{
            .block-container {{
                background: rgba(15, 15, 15, 0.85); /* Berubah jadi hitam transparan */
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            }}
        }}
        
        /* Membuat teks di dalam tabel bisa multi-line */
        [data-testid="stTable"] td {{
            white-space: pre-wrap !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_background("gedung_itb.jpg")

# 2. Header
col_logo, col_title = st.columns([1, 7])
with col_logo:
    try:
        # Trik HTML Base64 agar logo HD tidak di-compress oleh Streamlit
        with open("logo_itb.png", "rb") as f:
            logo_encoded = base64.b64encode(f.read()).decode()
        html_logo = f'<img src="data:image/png;base64,{logo_encoded}" style="width: 110px; height: auto;">'
        st.markdown(html_logo, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

with col_title:
    st.title("Sistem Rekomendasi Mata Kuliah ITB")
    st.write("Temukan mata kuliah pilihan berdasarkan silabus, jurusan pemberi, dan jadwal kelas.")
    st.info("🧠 **Mesin Rekomendasi AI:** Ditenagai oleh ekstraksi fitur **TF-IDF** (Term Frequency-Inverse Document Frequency) dan perhitungan jarak **Cosine Similarity**.")

# 3. Init System
@st.cache_resource
def init_system():
    return load_system()

with st.spinner("Memuat database..."):
    df, v_nama, m_nama, v_deskripsi, m_deskripsi = init_system()

if df is not None:
    # 4. Input User
    st.markdown("### 🔍 Filter Pencarian")
    col1, col2 = st.columns(2)
    with col1:
        daftar_jurusan = sorted([str(j).strip() for j in df['jurusan'].unique() if pd.notna(j) and str(j).lower() != 'nan' and str(j).strip() != ''])
        user_jurusan = st.selectbox("Pilih Jurusan Anda:", daftar_jurusan)
    with col2:
        query = st.text_input("Ketik Topik/Mata Kuliah:", placeholder="Contoh: Statistika, Lingkungan, Seni...")
        
# 5. Tombol Cari dan Session State (Ingatan Memori)
    # Membuat memori agar hasil pencarian dan halaman tidak hilang saat tombol next ditekan
    if 'hasil_rekomendasi' not in st.session_state:
        st.session_state.hasil_rekomendasi = pd.DataFrame()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'query_terakhir' not in st.session_state:
        st.session_state.query_terakhir = ""

    if st.button("Cari Rekomendasi", type="primary", use_container_width=True):
        if query:
            hasil = get_recommendations(
                query=query, 
                user_jurusan=user_jurusan, 
                df=df, 
                vec_nama=v_nama, 
                mat_nama=m_nama, 
                vec_deskripsi=v_deskripsi, 
                mat_deskripsi=m_deskripsi, 
                top_n=20 # <--- Diubah jadi 20 agar pas menjadi 2 halaman (10 per halaman)
            )
            # Simpan ke memori Streamlit
            st.session_state.hasil_rekomendasi = hasil
            st.session_state.query_terakhir = query
            st.session_state.current_page = 1 # Reset ke halaman 1 setiap kali cari baru
        else:
            st.warning("Silakan masukkan kata kunci.")

    # 6. Tampilkan Tabel dengan Fitur Pagination
    df_hasil = st.session_state.hasil_rekomendasi
    
    if not df_hasil.empty:
        st.markdown(f"#### ✅ Rekomendasi untuk: **'{st.session_state.query_terakhir}'**")
        
        # --- LOGIKA PAGINATION ---
        items_per_page = 10
        total_pages = (len(df_hasil) - 1) // items_per_page + 1
        
        # Memotong tabel sesuai dengan halaman saat ini
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_tampil = df_hasil.iloc[start_idx:end_idx]
        
        # TAMPILAN TABEL
        st.dataframe(
            df_tampil,
            width='stretch',
            column_config={
                "Jadwal Kelas": st.column_config.TextColumn(
                    "Jadwal & Dosen",
                    help="Daftar kelas, dosen pengampu, dan jadwal mingguan",
                    width="large",
                ),
                "Link Silabus": st.column_config.LinkColumn(
                    "SIX ITB", 
                    display_text="Lihat Silabus 🔗"
                )
            },
            hide_index=False 
        )
        
        # --- TOMBOL NAVIGASI BAWAH TABEL ---
        st.write("") # Memberi sedikit jarak
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.button("⬅️ Sebelumnya", use_container_width=True, disabled=(st.session_state.current_page == 1)):
                st.session_state.current_page -= 1
                st.rerun() # Memaksa web me-refresh untuk pindah halaman
                
        with col_page:
            # Teks penunjuk halaman di tengah
            st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 15px;'>Halaman <b>{st.session_state.current_page}</b> dari <b>{total_pages}</b></div>", unsafe_allow_html=True)
            
        with col_next:
            if st.button("Selanjutnya ➡️", use_container_width=True, disabled=(st.session_state.current_page == total_pages)):
                st.session_state.current_page += 1
                st.rerun()
                
    elif st.session_state.query_terakhir != "":
        # Jika hasil kosong tapi query sudah diketik
        st.warning("Tidak ditemukan mata kuliah yang relevan.")
        
# 7. Copyright Footer
footer_html = """
<style>
/* Tema Terang (Default) */
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: rgba(250, 250, 250, 0.95);
    color: #333;
    text-align: center;
    padding: 12px 0;
    font-size: 13px;
    border-top: 1px solid #ccc;
    z-index: 1000;
    line-height: 1.5;
}
.disclaimer {
    font-size: 11px;
    color: #666;
    font-style: italic;
    margin-bottom: 4px;
}

/* Tema Gelap (Night Mode) */
@media (prefers-color-scheme: dark) {
    .footer {
        background-color: rgba(20, 20, 20, 0.95);
        color: #eee;
        border-top: 1px solid #444;
    }
    .disclaimer {
        color: #aaa;
    }
}
</style>
<div class="footer">
    <div class="disclaimer">*Disclaimer: Data jadwal diambil dari Semester 1 2025/2026 dan Semester 2 2025/2026.</div>
    Dibuat untuk memenuhi Tugas Akhir <b>Tria Sania Oktavia (10122036)</b><br>
    di bawah bimbingan <b>Prof. Edy Tri Baskoro, S.Si., M.Sc., Ph.D.</b>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
st.markdown(footer_html, unsafe_allow_html=True)
