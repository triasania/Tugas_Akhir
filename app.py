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
        .block-container {{
            background: rgba(255, 255, 255, 0.93);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.03);
            margin-top: 2rem;
            margin-bottom: 6rem;
        }}
        /* Membuat teks di dalam tabel bisa multi-line (untuk jadwal) */
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
        
        # Atur lebar (width) di sini, misal 110px atau 120px
        html_logo = f'<img src="data:image/png;base64,{logo_encoded}" style="width: 110px; height: auto;">'
        st.markdown(html_logo, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo belum ada.")

with col_title:
    st.title("Sistem Rekomendasi Mata Kuliah Strata 1 Institut Teknologi Bandung")
    st.write("Temukan mata kuliah pilihan berdasarkan silabus, jurusan pemberi, dan jadwal kelas.")

st.divider()

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

    # 5. Tombol Cari
    if st.button("Cari Rekomendasi", type="primary", use_container_width=True):
        if query:
            hasil_rekomendasi = get_recommendations(
                query=query, 
                user_jurusan=user_jurusan, 
                df=df, 
                vec_nama=v_nama, 
                mat_nama=m_nama, 
                vec_deskripsi=v_deskripsi, 
                mat_deskripsi=m_deskripsi, 
                top_n=15
            )
            
            if not hasil_rekomendasi.empty:
                st.markdown(f"#### ✅ Rekomendasi untuk: **'{query}'**")
                
                # TAMPILAN TABEL DENGAN JADWAL
                st.dataframe(
                    hasil_rekomendasi,
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
                    hide_index=False # Agar ranking tetap terlihat di paling kiri
                )
            else:
                st.warning("Tidak ditemukan mata kuliah yang relevan.")
        else:
            st.warning("Silakan masukkan kata kunci.")

# 6. Copyright Footer
footer_html = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: rgba(255, 255, 255, 0.95);
    color: #333;
    text-align: center;
    padding: 15px 0;
    font-size: 13px;
    border-top: 1px solid #ccc;
    z-index: 1000;
    line-height: 1.6;
}
</style>
<div class="footer">
    Dibuat untuk memenuhi Tugas Akhir <b>Tria Sania Oktavia (10122036)</b><br>
    di bawah bimbingan <b>Prof. Edy Tri Baskoro, S.Si., M.Sc., Ph.D.</b>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
