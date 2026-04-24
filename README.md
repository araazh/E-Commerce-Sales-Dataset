# 🛍️ Dashboard Analisis Data E-Commerce Brazil 

Dashboard interaktif untuk menganalisis dataset **Brazilian E-Commerce Public Dataset by Olist** yang mencakup 100.000+ transaksi dari tahun 2016 hingga 2018 di berbagai marketplace Brazil.

---

## 📁 Struktur Proyek

```
submission/
├── dashboard/
│   ├── dashboard.py        # Aplikasi Streamlit
│   └── main_data.csv       # Dataset gabungan untuk dashboard
├── data/
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb          # Notebook analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                 # Link dashboard yang sudah di-deploy
```

## 🔍 Fitur Dashboard

- **Filter interaktif** — rentang waktu, status pesanan, dan negara bagian
- **Tab Kategori Produk** — analisis popularitas dan kepuasan pelanggan per kategori
- **Tab Efisiensi Pengiriman** — distribusi waktu pengiriman dan performa per wilayah
- **Tab Segmentasi Pelanggan** — analisis RFM dengan 4 segmen pelanggan
- **Tab Tren Penjualan** — tren bulanan, tahunan, dan pola per hari

---

## 🚀 Setup & Menjalankan Dashboard

### 1. Clone repository
```bash
git clone https://github.com/araazh/E-Commerce-Sales-Dataset.git
cd E-Commerce-Sales-Dataset
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan dashboard
```bash
cd dashboard
streamlit run dashboard.py
```

### 4. Buka di browser
Dashboard akan otomatis terbuka di `http://localhost:8501`

---

## 🌐 Live Dashboard

Dashboard sudah di-deploy dan dapat diakses di:

👉 **[Lihat Dashboard](https://e-commerce-sales-dataset.streamlit.app/)**


---

## 📦 Dependencies

```
streamlit
pandas
matplotlib
seaborn
babel
numpy
```

---

## 📂 Dataset

**Brazilian E-Commerce Public Dataset by Olist**
- Sumber: [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- Periode: 2016–2018
- Jumlah transaksi: ~100.000 pesanan
- Cakupan: informasi pesanan, produk, pelanggan, penjual, pembayaran, ulasan, dan pengiriman

---

## 👤 Author

**Azzahra Fitri Ramadhanti**  
Submission Proyek Fundamental Analisis Data — Dicoding
