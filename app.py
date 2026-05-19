import streamlit as st
import pandas as pd
from sistem_rekomendasi_buat_sidang import load_system, get_recommendations

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Rekomendasi Matkul ITB", layout="wide")

st.title("🎓 Sistem Rekomendasi Mata Kuliah ITB")
st.write("Temukan mata kuliah pilihan yang paling cocok untukmu berdasarkan silabus dan jadwal.")

# 2. Load Sistem
@st.cache_resource
def init_system():
    return load_system()

with st.spinner("Memuat database mata kuliah..."):
    df, v_nama, m_nama, v_deskripsi, m_deskripsi = init_system()

if df is None:
    st.error("Gagal memuat dataset. Pastikan file 'dataset_s1_efisien.csv' ada di folder yang sama.")
else:
    st.success("Sistem siap digunakan!")
    st.divider()

    # 3. Merakit Antarmuka Input User
    col1, col2 = st.columns(2)

    with col1:
        daftar_jurusan = sorted(df['jurusan'].unique())
        user_jurusan = st.selectbox("Pilih Jurusan Anda:", daftar_jurusan)
        
    with col2:
        query = st.text_input("Ketik Kata Kunci Topik/Mata Kuliah:", placeholder="Contoh: Statistika Dasar, Energi Terbarukan...")

    # 4. Tombol Cari
    if st.button("Cari Rekomendasi", type="primary"):
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
            
            st.subheader(f"Hasil Pencarian untuk: '{query}'")
            
            if not hasil_rekomendasi.empty:
                # Menampilkan satu dataframe dengan kolom link
                st.dataframe(
                    hasil_rekomendasi,
                    width='stretch',
                    column_config={
                        "Link Silabus": st.column_config.LinkColumn(
                            "Buka di SIX ITB", 
                            display_text="Lihat Silabus 🔗"
                        )
                    }
                )
            else:
                st.warning("Tidak ditemukan mata kuliah yang relevan.")
        else:
            st.warning("Mohon masukkan kata kunci pencarian terlebih dahulu.")