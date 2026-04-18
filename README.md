# 🛡️ FraudGuard: End-to-End SOC Analytics & Data Pipeline

> **Quick Navigation:** [English Version](#english-version) | [Türkçe Versiyon](#turkce-versiyon)

---

<a name="english-version"></a>
## 🇬🇧 English Version

# Project Overview
FraudGuard  is a professional-grade Security Operations Center  dashboard and data engineering pipeline. It simulates a financial ecosystem where thousands of credit card transactions are processed through a **Complex Rule Engine** to identify high-risk anomalies such as **Velocity Spikes**, **Location Jumps**, and **High-Value Fraud**.

# Architecture & Pipeline
1. **Extraction:** Generates 15,000+ synthetic transactions with realistic fraud scenarios.
2. **Transformation:** Feature engineering and automated risk scoring via Python (Pandas/NumPy).
3. **Loading:** Normalized data storage in an optimized **Star Schema** on SQLite.
4. **Visualization:** High-performance, dedicated **Dark Mode** UI built with **Streamlit** and **Plotly**.

# Key Features
- **Dynamic File Processing:** Seamless support for both local SQL databases and real-time CSV uploads for instant analysis.
- **Strategic Risk Matrix:** Interactive scatter analysis correlating transaction amounts with risk scores for forensic depth.
- **Time-Series Intelligence:** Hourly fraud density analysis to identify critical "attack windows" (Heatmap & Line Analysis).
- **Smart Data Explorer:** Forensic search tool with visual progress bars for risk scores and instant CSV export.
- **SOC Optimized UI:** Strictly Dark Mode interface designed for 24/7 security operation monitoring.

# Tech Stack
- **Language:** Python 3.12
- **Data Ops:** Pandas, NumPy
- **Database:** SQLite (Star Schema Design)
- **UI/UX:** Streamlit (Custom CSS), Plotly Express

# Installation & Usage

# Install dependencies
pip install streamlit pandas plotly numpy

# Run the data pipeline (Generate & Load)
python src/loader.py

# Launch the SOC Dashboard
streamlit run src/app.py


<a name="turkce-version"></a>
## 🇹🇷 Türkçe Versiyon

# Proje Özeti
FraudGuard , finansal işlemlerdeki dolandırıcılık vakalarını tespit etmek, analiz etmek ve raporlamak için geliştirilmiş uçtan uca bir Veri Mühendisliği hattı paneli çözümüdür. Sistem, binlerce işlemi karmaşık bir iş kuralı motorundan geçirerek Hız İhlalleri, Lokasyon Kaymaları ve Yüksek Tutarlı Fraud girişimlerini anlık olarak skorlar.

# Mimari ve Veri Hattı
1. **Çıkarım (Extract): Gerçekçi fraud senaryolarını içeren 15.000+ sentetik işlem üretimi.
2. **Dönüştürme (Transform): Python (Pandas/NumPy) ile özellik mühendisliği ve otomatik risk puanlama süreçleri.
3. **Yükleme (Load): Verilerin SQLite üzerinde optimize edilmiş Yıldız Şema (Star Schema) yapısına aktarılması.
4. **Görselleştirme: Streamlit ve Plotly kullanılarak geliştirilmiş, profesyonel arayüzü.

# Öne Çıkan Özellikler
- **Dynamic File Processing:** Seamless support for both local SQL databases and real-time CSV uploads for instant analysis.
- **Strategic Risk Matrix:** Interactive scatter analysis correlating transaction amounts with risk scores for forensic depth.
- **Time-Series Intelligence:** Hourly fraud density analysis to identify critical "attack windows" (Heatmap & Line Analysis).
- **Smart Data Explorer:** Forensic search tool with visual progress bars for risk scores and instant CSV export.
- **SOC Optimized UI:** Strictly Dark Mode interface designed for 24/7 security operation monitoring.

# Kullanılan Teknolojiler
- **Dil:** Python 3.12
- **Veri Mühendisliği:** Pandas, NumPy
- **Veri tabanı:** SQLite (Yıldız Şema Tasarımı)
- **UI/UX:** Streamlit , Plotly Express

#  Kurulum

# Bağımlılıkları yükleyin
pip install streamlit pandas plotly numpy

# Veri hattını çalıştırın (Üretim ve Yükleme)
python src/loader.py

# Paneli başlatın
streamlit run src/app.py
