import sqlite3
import pandas as pd
import os

DATA_DIR = "../data"
DB_PATH = f"{DATA_DIR}/fraud_warehouse.db"

def create_schema(cursor):
    print("🏗️ Veritabanı Yıldız Şeması (Star Schema) Kuruluyor...")
    cursor.executescript('''
    DROP TABLE IF EXISTS fact_transactions;
    DROP TABLE IF EXISTS dim_users;
    DROP TABLE IF EXISTS dim_merchants;
    DROP TABLE IF EXISTS dim_date;

    -- Müşteri Bilgileri
    CREATE TABLE dim_users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        home_city TEXT,
        account_balance REAL
    );

    -- İşyeri Bilgileri
    CREATE TABLE dim_merchants (
        merchant_id TEXT PRIMARY KEY,
        merchant_name TEXT,
        category TEXT,
        merchant_city TEXT
    );

    -- Zaman Bilgileri (Analiz için çok önemli)
    CREATE TABLE dim_date (
        date_id TEXT PRIMARY KEY,
        full_date DATETIME,
        hour INTEGER,
        day_of_week INTEGER
    );

    -- Merkez Tablo (Gerçekler)
    CREATE TABLE fact_transactions (
        transaction_id TEXT PRIMARY KEY,
        user_id TEXT,
        merchant_id TEXT,
        date_id TEXT,
        amount REAL,
        risk_score INTEGER,
        system_decision TEXT,
        is_fraud INTEGER,
        scenario TEXT,
        triggered_rules TEXT,
        FOREIGN KEY(user_id) REFERENCES dim_users(user_id),
        FOREIGN KEY(merchant_id) REFERENCES dim_merchants(merchant_id),
        FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
    );
    ''')

def load_data():
    print("📦 Veriler Okunuyor ve Normalize Ediliyor...")
    df_processed = pd.read_csv(f"{DATA_DIR}/processed_transactions.csv", parse_dates=['transaction_date'])
    df_users_raw = pd.read_csv(f"{DATA_DIR}/users.csv")
    df_merchants_raw = pd.read_csv(f"{DATA_DIR}/merchants.csv")

    # 1. Boyut Tabloları (Dimension) Hazırlığı
    df_users = df_users_raw[['user_id', 'name', 'age', 'home_city', 'account_balance']].drop_duplicates()
    df_merchants = df_merchants_raw[['merchant_id', 'merchant_name', 'category', 'merchant_city']].drop_duplicates()

    df_processed['date_id'] = df_processed['transaction_date'].dt.strftime('%Y%m%d%H')
    df_date = df_processed[['date_id', 'transaction_date']].drop_duplicates('date_id').copy()
    df_date['full_date'] = df_date['transaction_date']
    df_date['hour'] = df_date['transaction_date'].dt.hour
    df_date['day_of_week'] = df_date['transaction_date'].dt.dayofweek
    df_date = df_date.drop(columns=['transaction_date'])

    # 2. Gerçek (Fact) Tablosu Hazırlığı
    fact_cols = ['transaction_id', 'user_id', 'merchant_id', 'date_id', 'amount', 
                 'risk_score', 'system_decision', 'is_fraud', 'scenario', 'triggered_rules']
    df_facts = df_processed[fact_cols]

    # 3. Veritabanına Yazma
    print("💾 Veriler SQLite'a Yazılıyor (INSERT)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    create_schema(cursor)

    df_users.to_sql('dim_users', conn, if_exists='append', index=False)
    df_merchants.to_sql('dim_merchants', conn, if_exists='append', index=False)
    df_date.to_sql('dim_date', conn, if_exists='append', index=False)
    df_facts.to_sql('fact_transactions', conn, if_exists='append', index=False)

    print(f"\n✅ BAŞARILI! Data Warehouse hazır: {DB_PATH}")
    
    # 4. İş Analisti Test Sorgusu
    test_query = """
    SELECT 
        scenario as Fraud_Senaryosu,
        COUNT(*) as Toplam_Girisim,
        SUM(CASE WHEN system_decision = 'FRAUD_ENGEL' THEN 1 ELSE 0 END) as Yakalanan,
        ROUND((SUM(CASE WHEN system_decision = 'FRAUD_ENGEL' THEN 1.0 ELSE 0 END) / COUNT(*)) * 100, 1) as Basari_Orani
    FROM fact_transactions
    WHERE is_fraud = 1
    GROUP BY scenario
    ORDER BY Basari_Orani ASC;
    """
    print("\n--- 🔍 SENARYO BAZLI YAKALAMA PERFORMANSI ---")
    print(pd.read_sql(test_query, conn).to_string(index=False))
    conn.close()

if __name__ == "__main__":
    load_data()