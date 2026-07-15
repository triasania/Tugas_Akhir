# Sistem Rekomendasi Mata Kuliah Pilihan Strata 1 ITB Kurikulum 2024

Repositori ini berisi kode sumber, dataset, dan purwarupa sistem pendukung keputusan berbasis web untuk rekomendasi mata kuliah pilihan Strata 1 di Institut Teknologi Bandung (ITB) menggunakan pendekatan *Content-Based Filtering*. Penelitian ini merupakan bagian dari Tugas Akhir Program Studi Sarjana Matematika, Fakultas Matematika dan Ilmu Pengetahuan Alam (FMIPA) ITB.

---

## 📂 Struktur Repositori & Deskripsi File

Berikut adalah daftar berkas yang terdapat di dalam repositori ini beserta fungsi utamanya:

*   **`app.py`**: Skrip utama aplikasi web interaktif yang dibangun menggunakan kerangka kerja *Streamlit*.
*   **`sistem_rekomendasi_buat_sidang.py`**: Modul inti pemrosesan data, pemodelan matriks *TF-IDF*, *Query Expansion*, dan kalkulasi *Cosine Similarity*.
*   **`requirements.txt`**: Daftar pustaka (*libraries*) Python yang dibutuhkan untuk menjalankan sistem.
*   **`dataset_s1_efisien.csv`**: Berkas master dataset kurikulum S1 ITB Kurikulum 2024 (silabus, bahan kajian, CPMK, dan jadwal kelas).
*   **`knowledge_base.csv`**: Pangkalan data pendukung atau kamus domain spesifik sistem.
*   **`daftar_wajib/`**: Direktori yang memuat data referensi mata kuliah wajib per program studi.
*   **`daftar_wajib.zip`**: Arsip terkompresi dari direktori data mata kuliah wajib.
*   **`data_kuesioner.csv`**: Data ordinal hasil uji kepuasan pengguna (*User Acceptance Testing* / UAT) dan uji reliabilitas *Cronbach's Alpha*.
*   **`logo_itb.png` & `gedung_itb.jpg`**: Aset visual pendukung untuk antarmuka (*UI*) aplikasi web.
*   **`__pycache__/`**: Direktori pen缓存 (cache) internal dari interpreter Python.

---

## 🚀 Cara Menjalankan Program

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/triasania/Tugas_Akhir.git](https://github.com/triasania/Tugas_Akhir.git)
    cd Tugas_Akhir
    ```

2.  **Install dependensi yang diperlukan:**
    Pastikan Anda sudah menginstal Python, kemudian jalankan perintah berikut di terminal:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Jalankan aplikasi berbasis web (*Streamlit*):**
    ```bash
    streamlit run app.py
    ```

---

## 🌐 Tautan Akses Online
Purwarupa sistem ini juga telah dideploy dan dapat diakses secara langsung melalui tautan berikut:
*   **Website Aplikasi:** [Streamlit Cloud App](https://sistem-rekomendasi-mata-kuliah-itb.streamlit.app/)

---

## 👩‍💻 Pembuat
*   **Nama:** Tria Sania Oktavia
*   **NIM:** 10122036
*   **Program Studi:** Matematika
*   **Institusi:** Institut Teknologi Bandung (ITB)
*   **Dosen Pembimbing:** Prof. Edy Tri Baskoro, M.Sc., Ph.D.
