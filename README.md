# Bike Sharing Dashboard

## Deskripsi Proyek

```
Proyek ini bertujuan untuk menganalisis pola peminjaman sepeda berdasarkan faktor musim, kondisi cuaca, dan waktu (jam) menggunakan dataset Bike Sharing.

Analisis ini dilakukan untuk memahami perilaku pengguna serta membantu optimalisasi distribusi sepeda.
```

## Insight Utama

```
1. Pengaruh Musim & Cuaca
Musim Fall (gugur) memiliki peminjaman tertinggi
Cuaca cerah meningkatkan peminjaman hingga 2–3× lebih tinggi dibanding hujan

2. Pola Peminjaman per Jam
Hari kerja: puncak pada jam 08.00 dan 17.00–18.00 (jam berangkat & pulang kerja)
Hari libur: puncak pada jam 12.00–14.00 (aktivitas rekreasi)

3. Faktor yang Mempengaruhi
Suhu memiliki pengaruh positif terhadap peminjaman
Kecepatan angin menurunkan minat pengguna
Cuaca menjadi faktor paling dominan dibanding tipe hari
```

## Setup Environment - Anaconda

```
conda create --name bike-ds python=3.9
conda activate bike-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
pip install -r requirements.txt
```

## Run steamlit app

```
streamlit run dashboard.py
```

## Struktur Proyek

```
submission/
├── dashboard/
|   ├── dashboard.py
|   └── main_data.csv
├── data/
|   ├── day.csv
|   └── hour.csv
├── notebook.ipynb
├── README.md
└── requirements.txt
```
