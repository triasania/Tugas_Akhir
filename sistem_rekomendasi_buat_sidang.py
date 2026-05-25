import pandas as pd
import os
import re
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

import pandas as pd

# PETA JURUSAN (Untuk Heuristic Boosting / Prioritas Sorting)
# Format huruf kecil semua sesuai daftar prodi ITB
DOMAIN_JURUSAN = {
    # === RUMPUN MATEMATIKA, DATA & STATISTIKA ===
    "statistika": ["matematika", "aktuaria"],
    "peluang": ["matematika", "aktuaria"],
    "data": ["matematika", "aktuaria", "teknik informatika", "sistem dan teknologi informasi"],
    "aljabar": ["matematika"],
    "kalkulus": ["matematika", "fisika"],
    "optimasi": ["matematika", "teknik industri"],
    
    # === RUMPUN INFORMATIKA & KOMPUTER ===
    "komputer": ["teknik informatika", "sistem dan teknologi informasi", "teknik elektro"],
    "pemrograman": ["teknik informatika", "sistem dan teknologi informasi"],
    "machine_learning": ["teknik informatika", "sistem dan teknologi informasi", "matematika"],
    "ai": ["teknik informatika", "sistem dan teknologi informasi"],
    "algoritma": ["teknik informatika", "sistem dan teknologi informasi", "matematika"],
    "jaringan_komputer": ["teknik telekomunikasi", "teknik informatika", "sistem dan teknologi informasi"],
    "keamanan_siber": ["sistem dan teknologi informasi", "teknik informatika"],
    
    # === RUMPUN FISIKA & ASTRONOMI ===
    "fisika": ["fisika", "teknik fisika"],
    "kuantum": ["fisika"],
    "astronomi": ["astronomi"],
    "tata_surya": ["astronomi"],
    "bintang": ["astronomi"],
    "mekanika": ["fisika", "teknik mesin", "teknik dirgantara"],
    
    # === RUMPUN KIMIA & MATERIAL ===
    "kimia": ["kimia", "teknik kimia"],
    "material": ["teknik material", "kimia", "teknik metalurgi"],
    "polimer": ["teknik material", "kimia", "teknik kimia"],
    "logam": ["teknik metalurgi", "teknik material"],
    
    # === RUMPUN BIOLOGI, HAYATI & PANGAN ===
    "biologi": ["biologi", "mikrobiologi", "rekayasa hayati"],
    "genetika": ["biologi", "mikrobiologi", "rekayasa kehutanan", "rekayasa hayati"],
    "mikroba": ["mikrobiologi", "rekayasa hayati"],
    "pangan": ["teknik pangan", "teknologi pasca panen", "rekayasa pertanian"],
    "pertanian": ["rekayasa pertanian", "teknologi pasca panen"],
    "kehutanan": ["rekayasa kehutanan"],
    
    # === RUMPUN FARMASI & KESEHATAN ===
    "farmasi": ["sains dan teknologi farmasi", "farmasi klinik dan komunitas"],
    "obat": ["sains dan teknologi farmasi", "farmasi klinik dan komunitas"],
    "klinis": ["farmasi klinik dan komunitas"],
    "medis": ["teknik biomedis", "sains dan teknologi farmasi"],
    "anatomi": ["teknik biomedis", "biologi"],
    
    # === RUMPUN KEBUMIAN, LINGKUNGAN & CUACA ===
    "bumi": ["teknik geologi", "teknik geofisika", "teknik geodesi dan geomatika"],
    "lingkungan": ["teknik lingkungan", "rekayasa infrastruktur lingkungan"],
    "cuaca": ["meteorologi"],
    "laut": ["oseanografi", "teknik kelautan"],
    "gempa": ["teknik geofisika", "teknik geologi", "teknik sipil"],
    "peta": ["teknik geodesi dan geomatika", "perencanaan wilayah dan kota"],
    "polusi": ["teknik lingkungan", "rekayasa infrastruktur lingkungan"],
    
    # === RUMPUN ENERGI & PERTAMBANGAN ===
    "tambang": ["teknik pertambangan"],
    "minyak": ["teknik perminyakan"],
    "gas": ["teknik perminyakan", "teknik kimia"],
    "energi_terbarukan": ["teknik bioenergi dan kemurgi", "teknik tenaga listrik", "teknik fisika"],
    "listrik": ["teknik tenaga listrik", "teknik elektro"],
    
    # === RUMPUN MESIN, DIRGANTARA & MANUFAKTUR ===
    "mesin": ["teknik mesin", "teknik dirgantara"],
    "pesawat": ["teknik dirgantara"],
    "terbang": ["teknik dirgantara"],
    "manufaktur": ["teknik mesin", "teknik industri"],
    "robotika": ["teknik elektro", "teknik mesin", "teknik informatika"],
    
    # === RUMPUN INFRASTRUKTUR & SIPIL ===
    "bangunan": ["teknik sipil", "arsitektur"],
    "konstruksi": ["teknik sipil", "arsitektur"],
    "jalan": ["teknik sipil"],
    "kota": ["perencanaan wilayah dan kota", "arsitektur"],
    "air": ["teknik dan pengelolaan sumber daya air", "teknik lingkungan", "teknik sipil"],
    
    # === RUMPUN INDUSTRI, BISNIS & MANAJEMEN ===
    "industri": ["teknik industri", "manajemen rekayasa"],
    "bisnis": ["manajemen", "kewirausahaan", "manajemen rekayasa"],
    "ekonomi": ["manajemen", "kewirausahaan"],
    "manajemen": ["manajemen", "manajemen rekayasa"],
    "kewirausahaan": ["kewirausahaan", "manajemen"],
    "logistik": ["teknik industri", "manajemen"],
    
    # === RUMPUN SENI & DESAIN ===
    "seni": ["seni rupa", "kriya", "desain interior", "desain komunikasi visual"],
    "desain": ["desain interior", "desain komunikasi visual", "desain produk", "arsitektur"],
    "visual": ["desain komunikasi visual", "seni rupa"],
    "interior": ["desain interior", "arsitektur"],
    "kriya": ["kriya", "seni rupa"]
}

# Daftar kata kunci dan sinonimnya (Dikelompokkan per Rumpun Ilmu)
data_kb = {
    "kata_kunci": [
        # === RUMPUN MATEMATIKA & STATISTIKA ===
        "statistika", "peluang", "aljabar", "kalkulus", "geometri",
        "matematika_diskrit", "optimasi", "topologi", "kriptografi", "analisis_numerik",
        "statistika_multivariat", "riset_operasi", "persamaan_diferensial",

        # === RUMPUN ILMU KOMPUTER & INFORMATIKA ===
        "machine_learning", "data_mining", "pemrograman", "basis_data", "kecerdasan_buatan",
        "jaringan_komputer", "keamanan_siber", "rekayasa_perangkat_lunak", "sistem_operasi",
        "cloud_computing", "iot", "visi_komputer", "nlp", "struktur_data", "algoritma",

        # === RUMPUN FISIKA & ASTRONOMI ===
        "mekanika", "termodinamika", "kuantum", "elektromagnetik", "optik",
        "astrofisika", "geofisika", "astronomi", "tata_surya", "kosmologi",
        "fisika_material", "fisika_inti", "fluida",

        # === RUMPUN TEKNIK & INDUSTRI ===
        "energi_terbarukan", "manufaktur", "ergonomi", "rantai_pasok", "robotika",
        "elektronika", "telekomunikasi", "teknik_sipil", "arsitektur", "material",
        "mekatronika", "hidrologi", "geoteknik",

        # === RUMPUN KIMIA, BIOLOGI & FARMASI ===
        "kimia_organik", "kimia_analitik", "biokimia", "polimer", "termodinamika_kimia",
        "biologi", "genetika", "mikrobiologi", "ekologi", "anatomi",
        "farmasi", "farmakologi", "botani", "zoologi",

        # === RUMPUN LINGKUNGAN & KEBUMIAN ===
        "lingkungan", "geologi", "meteorologi", "oseanografi", "mitigasi_bencana",
        "konservasi", "polusi", "klimatologi", "vulkanologi",

        # === RUMPUN EKONOMI, BISNIS & MANAJEMEN ===
        "ekonomi", "akuntansi", "manajemen", "kewirausahaan", "pemasaran",
        "keuangan", "investasi", "sumber_daya_manusia", "strategi_bisnis", "makroekonomi",

        # === RUMPUN SOSIAL, HUMANIORA & SENI (MKU) ===
        "komunikasi", "jurnalisme", "sastra", "desain", "seni",
        "sejarah", "filsafat", "hukum", "sosiologi", "psikologi",
        "pancasila", "kewarganegaraan", "bahasa_inggris", "bahasa_indonesia"
    ],
    "sinonim": [
        # === RUMPUN MATEMATIKA & STATISTIKA ===
        "peluang, distribusi, peubah_acak, variansi, hipotesis, data, regresi, anova, inferensi",
        "probabilitas, kombinatorika, permutasi, acak, stokastik",
        "matriks, vektor, linear, persamaan, ruang_vektor, eigen, transformasi, skalar",
        "turunan, integral, limit, diferensial, peubah, multivariabel, fungsi, kontinu",
        "ruang, bangun, dimensi, sudut, trigonometri, titik, garis, kurva",
        "himpunan, graf, logika, kombinatorik, pohon, algoritma_diskrit",
        "maksimasi, minimasi, program_linear, simplex, metaheuristik, kendala",
        "ruang_topologi, metrik, kekontinuan, himpunan_terbuka, kompak",
        "enkripsi, dekripsi, sandi, keamanan_data, cipher, rsa, rahasia",
        "hampiran, iterasi, galat, interpolasi, metode_numerik, komputasi_matematika",
        "pca, analisis_faktor, diskriminan, klaster, manova, multivariabel",
        "antrian, simulasi, optimasi_sistem, pemodelan_sistem, markov",
        "pd_biasa, pd_parsial, nilai_awal, syarat_batas, orde",

        # === RUMPUN ILMU KOMPUTER & INFORMATIKA ===
        "ai, kecerdasan_buatan, klasifikasi, prediksi, neural_network, deep_learning, clustering",
        "preprocessing, clustering, klasifikasi, ekstraksi, big_data, pola, asosiasi",
        "coding, kode, sintaks, python, c++, java, web, developer, aplikasi",
        "database, sql, nosql, query, relasional, erd, normalisasi, server_data",
        "ai, sistem_pakar, logika_fuzzy, nlp, visi_komputer, robotika, agen_cerdas",
        "tcp_ip, routing, internet, nirkabel, protokol, server, bandwidth, lan, wan",
        "kriptografi, hacker, malware, firewall, enkripsi, privasi, forensik, pentest",
        "rpl, agile, scrum, sdlc, testing, uml, desain_sistem, arsitektur_software",
        "os, linux, windows, kernel, thread, memori, sinkronisasi, deadlock",
        "komputasi_awan, aws, azure, docker, kubernetes, virtualisasi, hosting",
        "internet_of_things, sensor, aktuator, mikrokontroler, arduino, smart_home",
        "pengolahan_citra, deteksi_objek, segmentasi, piksel, kamera, image_processing",
        "pemrosesan_bahasa_alami, teks, chatbot, terjemahan, sentimen",
        "array, linked_list, stack, queue, tree, graph, hash",
        "sorting, searching, kompleksitas, big_o, rekursif, dinamis",

        # === RUMPUN FISIKA & ASTRONOMI ===
        "statika, dinamika, kinematika, gaya, torsi, momentum, energi, gerak",
        "kalor, suhu, entropi, entalpi, mesin_kalor, gas_ideal, perpindahan_panas",
        "foton, planck, schrodinger, partikel, gelombang, atom, ketidakpastian",
        "listrik, magnet, tegangan, arus, sirkuit, maxwell, induksi",
        "cahaya, lensa, cermin, difraksi, interferensi, refraksi, fotonika",
        "bintang, galaksi, alam_semesta, gravitasi, lubang_hitam, eksoplanet",
        "seismik, gravitasi, magnetik, eksplorasi, struktur_bumi, gempa",
        "observasi, teleskop, langit, konstelasi, tata_surya, planet",
        "matahari, planet, bulan, asteroid, komet, meteor",
        "big_bang, pembentukan_alam_semesta, dark_matter, dark_energy, ruang_waktu",
        "polimer, keramik, komposit, nanomaterial, kristal, semikonduktor",
        "radioaktivitas, reaktor, fusi, fisi, radiasi, isotop",
        "cairan, gas, viskositas, aerodinamika, hidrostatika, bernoulli",

        # === RUMPUN TEKNIK & INDUSTRI ===
        "solar, angin, panas_bumi, geothermal, biomassa, lingkungan, surya, hidro",
        "cnc, pemesinan, pengecoran, pengelasan, fabrikasi, produksi, pabrik",
        "k3, keselamatan_kerja, postur, biomekanika, lingkungan_kerja, human_factor",
        "supply_chain, logistik, inventori, gudang, transportasi, distribusi",
        "otomasi, mekatronika, sensor, aktuator, kontrol_otomatis, ai_robot",
        "semikonduktor, transistor, pcb, sirkuit_digital, sirkuit_analog, mikrokontroler",
        "sinyal, modulasi, antena, serat_optik, seluler, transmisi, jaringan_komunikasi",
        "beton, baja, struktur, jembatan, jalan, konstruksi, bangunan",
        "bangunan, tata_ruang, fasad, interior, lanskap, urban_design, estetika_bangunan",
        "logam, komposit, korosi, kekuatan_bahan, tegangan_regangan",
        "integrasi_sistem, mesin, elektronik, kontrol, otomatisasi",
        "air, sungai, banjir, drainase, curah_hujan, siklus_air",
        "tanah, fondasi, longsor, mekanika_tanah, batuan",

        # === RUMPUN KIMIA, BIOLOGI & FARMASI ===
        "karbon, hidrokarbon, sintesis, gugus_fungsi, reaksi_organik, polimerisasi",
        "titrasi, spektroskopi, kromatografi, pemisahan, instrumen_kimia, kuantitatif",
        "enzim, protein, metabolisme, karbohidrat, lipid, dna, rna",
        "makromolekul, plastik, karet, sintetik, material_cerdas",
        "entalpi_reaksi, energi_bebas, kesetimbangan_kimia, fasa",
        "sel, genetika, evolusi, ekosistem, makhluk_hidup, organisme",
        "dna, kromosom, mutasi, pewarisan_sifat, rekayasa_genetika, genom",
        "bakteri, virus, jamur, patogen, mikroskopis, kultur",
        "lingkungan, habitat, populasi, rantai_makanan, keanekaragaman_hayati",
        "organ, jaringan, kerangka, otot, tubuh, fisiologi",
        "obat, apotek, resep, klinis, medis, penyembuhan, terapi",
        "efek_obat, dosis, toksikologi, farmakokinetik, farmakodinamik",
        "tumbuhan, tanaman, fotosintesis, flora, vegetasi",
        "hewan, fauna, vertebrata, invertebrata, perilaku_hewan",

        # === RUMPUN LINGKUNGAN & KEBUMIAN ===
        "ekosistem, polusi, limbah, iklim, pemanasan_global, amdal, hijau",
        "batuan, mineral, tektonik, bumi, sedimen, stratigrafi, fosil",
        "cuaca, iklim, atmosfer, hujan, awan, angin, prakiraan_cuaca",
        "laut, gelombang, arus_laut, pesisir, terumbu_karang, pasang_surut",
        "bencana, gempa, tsunami, banjir, evakuasi, risiko_bencana, penanggulangan",
        "perlindungan, pelestarian, satwa_liar, taman_nasional, hutan",
        "pencemaran, limbah_cair, udara, tanah, emisi, toksik",
        "perubahan_iklim, suhu_global, el_nino, la_nina, cuaca_ekstrem",
        "gunung_api, magma, lava, erupsi, kawah, vulkanik",

        # === RUMPUN EKONOMI, BISNIS & MANAJEMEN ===
        "mikroekonomi, makroekonomi, moneter, inflasi, pasar, permintaan, penawaran",
        "pembukuan, laporan_keuangan, audit, pajak, neraca, laba_rugi, biaya",
        "strategi, sdm, operasional, pemasaran, organisasi, kepemimpinan, risiko",
        "bisnis, startup, inovasi, produk, pasar, modal, ventura, kelayakan",
        "konsumen, branding, promosi, iklan, penjualan, riset_pasar, digital_marketing",
        "investasi, saham, obligasi, perbankan, portofolio, risiko_keuangan",
        "saham, reksa_dana, pasar_modal, return, risiko, dividen, trading",
        "rekrutmen, pelatihan, kinerja, kompensasi, karyawan, personalia",
        "visi, misi, keunggulan_kompetitif, analisis_swot, model_bisnis",
        "pertumbuhan_ekonomi, pdb, pengangguran, kebijakan_fiskal, ekspor_impor",

        # === RUMPUN SOSIAL, HUMANIORA & SENI (MKU) ===
        "presentasi, retorika, persuasi, interpersonal, publik, lisan, tulisan, verbal",
        "berita, peliputan, media, artikel, wawancara, opini, reportase, redaksi",
        "puisi, cerpen, novel, fiksi, narasi, imajinasi, prosa, drama, teks",
        "visual, grafis, tipografi, estetika, warna, komposisi, ui, ux",
        "rupa, musik, tari, teater, lukis, patung, kriya, kontemporer",
        "masa_lalu, peradaban, kuno, modern, kolonial, revolusi, arsip, peninggalan",
        "logika, etika, epistemologi, ontologi, moral, pemikiran, eksistensialisme",
        "perdata, pidana, tata_negara, internasional, konstitusi, regulasi, undang_undang",
        "masyarakat, interaksi, budaya, kelas_sosial, institusi, urban, demografi",
        "kognitif, klinis, perkembangan, sosial, perilaku, mental, emosi, terapi",
        "ideologi, dasar_negara, uud_1945, bhinneka_tunggal_ika, nkri",
        "kewajiban_warga_negara, hak_asasi, demokrasi, politik, identitas_nasional",
        "grammar, reading, writing, listening, speaking, toefl, ielts, vocabulary",
        "ejaan, tata_bahasa, paragraf, esai, karya_tulis_ilmiah, eyd"
    ]
}

# Cek apakah jumlah kata_kunci dan sinonim sama
if len(data_kb["kata_kunci"]) == len(data_kb["sinonim"]):
    print(f"Total kata kunci siap di-generate: {len(data_kb['kata_kunci'])}")
    # Buat DataFrame dan simpan ke CSV
    df_kb = pd.DataFrame(data_kb)
    df_kb.to_csv("knowledge_base.csv", index=False)
    print("File 'knowledge_base.csv' super lengkap berhasil dibuat!")
else:
    print("Error: Jumlah kata_kunci dan sinonim tidak sama. Cek kembali kodenya.")

# ==========================================
# 1. KONFIGURASI
# ==========================================
FILE_DATASET = "dataset_s1_efisien.csv" 
FILE_KB = "knowledge_base.csv"
ROOT_WAJIB_FOLDER = "daftar_wajib" 

BLACKLIST_KEYWORDS = [
    "tugas akhir", "skripsi", "tesis", "disertasi",
    "kerja praktek", "kerja praktik", "magang",
    "seminar", "proposal", "sidang",
    "kuliah kerja", "kuliah lapangan", "ekskursi",
    "studi mandiri", "proyek mandiri", "pengayaan",
    "capstone", "pembinaan", "kolokium"
]

SPECIAL_PHRASES = {
    "machine learning": "machine_learning",
    "kecerdasan buatan": "kecerdasan_buatan",
    "data mining": "data_mining",
    "statistika dasar": "statistika_dasar",
    "energi terbarukan": "energi_terbarukan"
}

BOBOT_NAMA = 0.8       
BOBOT_DESKRIPSI = 0.2  

nltk.download('stopwords', quiet=True)

list_stopwords = stopwords.words('indonesian')

# list_stopwords = [
#    "yang", "di", "ke", "dari", "pada", "dalam", "untuk", "dengan", "dan", "atau", "ini", "itu", "juga", "sudah", "saya", "anda", "dia", "mereka", "kita", "kami", "akan", "bisa", "ada", "tidak", "belum", "bukan"]

list_stopwords.extend([
    "mahasiswa", "mampu", "memahami", "menjelaskan", "menggunakan",
    "capaian", "pembelajaran", "bahan", "kajian", "kuliah", "mata",
    "prasyarat", "deskripsi", "topik", "konsep", "dasar", "teori",
    "metode", "penerapan", "aplikasi", "analisis", "serta"
])

# ==========================================
# 2. FUNGSI UTILITAS
# ==========================================
def replace_special_phrases(text):
    pola_awalan = r'\b(tidak|bukan|belum|non|anti|tanpa|pra|pasca)[\s-]+(\w+)\b'
    text = re.sub(pola_awalan, r'\1_\2', text)
    for phrase, replacement in SPECIAL_PHRASES.items():
        text = re.sub(rf'\b{phrase}\b', replacement, text)
    return text

def text_preprocessing(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = replace_special_phrases(text)
    text = re.sub(r'[^\w\s_]', ' ', text)
    text = re.sub(r'\d+', '', text)
    words = text.split()
    clean_words = [w for w in words if w not in list_stopwords and len(w) > 2]
    return " ".join(clean_words)

def load_system():
    print("--- INISIALISASI SISTEM ---")
    if not os.path.exists(FILE_DATASET):
        print(f"Error: File {FILE_DATASET} tidak ditemukan.")
        return None, None, None, None, None

    print("1. Membaca CSV...")
    df = pd.read_csv(FILE_DATASET)
    df['kode_matkul'] = df['kode_matkul'].astype(str).str.strip()
    df['nama_matkul'] = df['nama_matkul'].astype(str).str.strip()
    df['jurusan'] = df['jurusan'].astype(str).str.strip()
    df['deskripsi'] = df['deskripsi'].fillna('')

    print("2. Membersihkan teks (Preprocessing)...")
    df['nama_bersih'] = df['nama_matkul'].apply(text_preprocessing)
    df['deskripsi_bersih'] = df['deskripsi'].apply(text_preprocessing)

    print("3. Membangun TF-IDF Nama...")
    vectorizer_nama = TfidfVectorizer(max_features=5000)
    matrix_nama = vectorizer_nama.fit_transform(df['nama_bersih'])

    print("4. Membangun TF-IDF Deskripsi...")
    vectorizer_deskripsi = TfidfVectorizer(max_features=15000)
    matrix_deskripsi = vectorizer_deskripsi.fit_transform(df['deskripsi_bersih'])

    print("--- SISTEM SIAP DIGUNAKAN ---\n")
    return df, vectorizer_nama, matrix_nama, vectorizer_deskripsi, matrix_deskripsi

def get_mandatory_codes(nama_jurusan):
    search_pattern = f"{ROOT_WAJIB_FOLDER}/wajib_{nama_jurusan}.txt"
    found_files = glob.glob(search_pattern)
    wajib_set = set()
    if not found_files:
        return wajib_set

    file_path = found_files[0]
    try:
        with open(file_path, 'r') as f:
            wajib_set = set(line.strip() for line in f)
            if "WI201X" in wajib_set:
                wajib_set.remove("WI201X")
    except Exception as e:
        print(f"Error: {e}")
    return wajib_set

def load_knowledge_base():
    """Membaca CSV Knowledge Base dan mengubahnya menjadi dictionary"""
    kb_dict = {}
    if not os.path.exists(FILE_KB):
        print(f"[INFO] File {FILE_KB} tidak ditemukan, fitur Query Expansion nonaktif.")
        return kb_dict

    df_kb = pd.read_csv(FILE_KB)
    for _, row in df_kb.iterrows():
        # Ambil kata kunci
        kata = str(row['kata_kunci']).strip().lower()
        # Ambil string sinonim, pisahkan berdasarkan koma, lalu bersihkan spasinya
        sinonim_list = [s.strip().lower() for s in str(row['sinonim']).split(',')]
        kb_dict[kata] = sinonim_list

    return kb_dict

# Load kamus pintar secara global agar bisa dipakai di mana saja
KNOWLEDGE_BASE = load_knowledge_base()


def expand_query(query):
    """Memperluas query dengan memberikan bobot ekstra (pengulangan) pada kata asli"""
    query_bersih = text_preprocessing(query)
    kata_kunci_list = query_bersih.split()
    
    # 1. Masukkan kata asli BEBERAPA KALI agar bobot bagian-nya lebih besar
    PENGULANGAN_KATA_ASLI = 1
    expanded_words = kata_kunci_list * PENGULANGAN_KATA_ASLI 
    
    # 2. Masukkan kata sinonim SATU KALI saja (sebagai tambahan bobot kecil)
    for kata in set(kata_kunci_list): # Pakai set() biar nggak dobel ngeceknya
        if kata in KNOWLEDGE_BASE:
            expanded_words.extend(KNOWLEDGE_BASE[kata])
            
    return " ".join(expanded_words)

# ==========================================
# 3. FUNGSI REKOMENDASI (DENGAN DOMAIN BOOSTING)
# ==========================================
def get_recommendations(query, user_jurusan, df, vec_nama, mat_nama, vec_deskripsi, mat_deskripsi, top_n=15):
    wajib_set = get_mandatory_codes(user_jurusan)
    
    clean_query = expand_query(query)
    print(f"[DEBUG] Query setelah diekspansi: '{clean_query}'")

    # A. Deteksi Jurusan Prioritas berdasarkan Query
    prioritas_jurusan = set()
    for kata in clean_query.split():
        if kata in DOMAIN_JURUSAN:
            prioritas_jurusan.update(DOMAIN_JURUSAN[kata])
    
    if prioritas_jurusan:
        print(f"[DEBUG] Jurusan yang di-boost ke atas: {prioritas_jurusan}")

    # B. Hitung Kemiripan TF-IDF
    query_vec_nama = vec_nama.transform([clean_query])
    sim_nama = cosine_similarity(query_vec_nama, mat_nama).flatten()

    query_vec_deskripsi = vec_deskripsi.transform([clean_query])
    sim_deskripsi = cosine_similarity(query_vec_deskripsi, mat_deskripsi).flatten()

    similarity_scores = (BOBOT_NAMA * sim_nama) + (BOBOT_DESKRIPSI * sim_deskripsi)
    
    # Ambil kandidat dalam jumlah besar dulu untuk disortir ulang
    candidate_indices = similarity_scores.argsort()[-(top_n * 10):][::-1] 

    temp_results = []
    
    # C. Kumpulkan dan Beri Label Prioritas
    for idx in candidate_indices:
        score = similarity_scores[idx]
        if score == 0:
            continue

        row = df.iloc[idx]
        kode = row['kode_matkul']
        nama_lower = row['nama_matkul'].lower()
        jurusan_matkul = str(row['jurusan'])
        jurusan_lower = jurusan_matkul.lower()
        
        category = "Pilihan Luar"

        # Cek Blacklist
        is_blacklisted = False
        for keyword in BLACKLIST_KEYWORDS:
            if keyword in nama_lower:
                is_blacklisted = True
                break
        if is_blacklisted: continue

        # Kategori Pengambilan
        if (kode in wajib_set) or (kode.startswith("WI201")):
            category = "Wajib (Sudah Diambil)"
        elif jurusan_matkul == user_jurusan:
            category = "Pilihan Dalam"

        # Cek apakah mata kuliah ini berasal dari jurusan prioritas
        is_priority = 0
        for pj in prioritas_jurusan:
            if pj in jurusan_lower:
                is_priority = 1
                break

        temp_results.append({
            "skor_mentah": score,
            "is_priority": is_priority,
            "Kode": kode,
            "Mata Kuliah": row['nama_matkul'],
            "Jurusan Asal": jurusan_matkul,
            "Kategori": category,
            "url": row['url']
        })

    # D. Lakukan Sorting Ulang (Prioritas Jurusan Dulu, Baru Skor TF-IDF)
    # Ini adalah "Sihir" yang diminta dosenmu
    temp_results.sort(key=lambda x: (x['is_priority'], x['skor_mentah']), reverse=True)

    # E. Ambil Top N dan Susun Hasil Akhir (Sembunyikan Skor, Buat Ranking)
    final_results = []
    for rank, item in enumerate(temp_results[:top_n], start=1):
        baris_asli = df[df['kode_matkul'] == item["Kode"]].iloc[0]
        jadwal_matkul = baris_asli.get('jadwal_lengkap', '-')
        
        final_results.append({
            "Ranking": rank,
            "Kode": item["Kode"],
            "Mata Kuliah": item["Mata Kuliah"],
            "Jurusan Asal": item["Jurusan Asal"],
            "Kategori": item["Kategori"],
            "Jadwal Kelas": jadwal_matkul,
            "Link Silabus": item["url"]
        })

    hasil_df = pd.DataFrame(final_results)
    
    # Atur agar kolom Ranking menjadi index utama di tabel
    if not hasil_df.empty:
        hasil_df = hasil_df.set_index("Ranking")

    return hasil_df
