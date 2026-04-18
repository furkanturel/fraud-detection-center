import pandas as pd
import numpy as np
import os

DATA_DIR = "../data"

def load_data():
    print("📥 Veriler Yükleniyor...")
    df_users = pd.read_csv(f"{DATA_DIR}/users.csv")
    df_merchants = pd.read_csv(f"{DATA_DIR}/merchants.csv")
    df_txn = pd.read_csv(f"{DATA_DIR}/transactions.csv", parse_dates=['transaction_date'])
    return df_users, df_merchants, df_txn

def feature_engineering(df):
    """Zaman Serisi ve Lokasyon Özelliklerini Üretir (Window Functions)"""
    print("⚙️ Feature Engineering (Özellik Çıkarımı) Yapılıyor...")
    
    # Kullanıcıya ve tarihe göre sırala (Zaman serisi analizi için şart)
    df = df.sort_values(by=['user_id', 'transaction_date']).reset_index(drop=True)
    
    # Bir önceki işlem bilgilerini aynı satıra taşı (LAG fonksiyonu)
    df['prev_txn_date'] = df.groupby('user_id')['transaction_date'].shift(1)
    df['prev_merchant_city'] = df.groupby('user_id')['merchant_city'].shift(1)
    
    # Süre ve Lokasyon Farkları
    df['minutes_since_last_txn'] = (df['transaction_date'] - df['prev_txn_date']).dt.total_seconds() / 60.0
    df['is_location_jump'] = (df['merchant_city'] != df['prev_merchant_city']) & (df['prev_merchant_city'].notna())
    
    # Hız İhlali (Velocity) için son 10 dakikadaki işlem sayısını hesapla
    # (Bunu Pandas ile yapmak biraz ustalık ister, rolling pencere kullanıyoruz)
    df = df.set_index('transaction_date')
    df['txn_count_10m'] = df.groupby('user_id')['transaction_id'].transform(
        lambda x: x.rolling('10min').count()
    )
    df = df.reset_index() # Index'i geri al
    
    return df

def apply_rule_engine(df):
    print("⚖️ Kural Motoru (Rule Engine) Çalıştırılıyor...")
    
    df['risk_score'] = 0
    df['triggered_rules'] = "" # Birden fazla kural tetiklenebilir
    
    # Kural 1: Location Impossibility (İmkansız Konum)
    # 60 dakikadan kısa sürede farklı şehirde işlem
    mask_location = (df['is_location_jump']) & (df['minutes_since_last_txn'] < 60)
    df.loc[mask_location, 'risk_score'] += 75
    df.loc[mask_location, 'triggered_rules'] += "[Location_Jump] "

    # Kural 2: Velocity Spike (Hız İhlali)
    # Son 10 dakika içinde 4'ten fazla işlem
    mask_velocity = df['txn_count_10m'] > 4
    df.loc[mask_velocity, 'risk_score'] += 60
    df.loc[mask_velocity, 'triggered_rules'] += "[Velocity_Spike] "

    # Kural 3: Card Testing (Mikro Deneme)
    # Son 10 dakika içinde 5 TL altı işlem
    mask_testing = (df['amount'] < 5) & (df['txn_count_10m'] > 1)
    df.loc[mask_testing, 'risk_score'] += 40
    df.loc[mask_testing, 'triggered_rules'] += "[Card_Testing] "

    # Kural 4: Midnight Round Amount (Gece Tam Sayı)
    # Gece 02:00-05:00 arası riskli sektörlerde küsüratsız büyük işlemler
    mask_midnight = (df['transaction_date'].dt.hour.isin([2, 3, 4])) & \
                    (df['amount'] >= 5000) & \
                    (df['amount'] % 1000 == 0) & \
                    (df['category'].isin(['Kuyumcu', 'Kripto/Finans', 'Elektronik']))
    df.loc[mask_midnight, 'risk_score'] += 85
    df.loc[mask_midnight, 'triggered_rules'] += "[Midnight_Round] "

    # Karar Aşaması: Eşik Değeri 70 olsun
    df['system_decision'] = np.where(df['risk_score'] >= 70, 'FRAUD_ENGEL', 'ONAYLANDI')
    
    # Boş kuralları temizle
    df['triggered_rules'] = df['triggered_rules'].replace("", "None")
    
    return df

def process_pipeline():
    df_users, df_merchants, df_txn = load_data()
    
    # 1. Tabloları Birleştir (JOIN)
    df_merged = df_txn.merge(df_users[['user_id', 'home_city']], on='user_id', how='left')
    df_merged = df_merged.merge(df_merchants[['merchant_id', 'category', 'merchant_city']], on='merchant_id', how='left')
    
    # 2. Özellik Üret ve Kuralları İşlet
    df_features = feature_engineering(df_merged)
    df_final = apply_rule_engine(df_features)
    
    # 3. Gereksiz Sütunları Temizle
    cols_to_drop = ['prev_txn_date', 'prev_merchant_city', 'is_location_jump']
    df_final = df_final.drop(columns=cols_to_drop, errors='ignore')
    
    # 4. Kaydet
    output_path = f"{DATA_DIR}/processed_transactions.csv"
    df_final.to_csv(output_path, index=False)
    
    print("\n--- 📈 ANALİZ SONUÇLARI ---")
    gercek_fraud = len(df_final[df_final['is_fraud'] == 1])
    sistemin_engelledigi = len(df_final[df_final['system_decision'] == 'FRAUD_ENGEL'])
    
    print(f"Toplam İşlem: {len(df_final)}")
    print(f"Veriye Gizlenen Gerçek Fraud: {gercek_fraud}")
    print(f"Kural Motorunun Yakaladığı: {sistemin_engelledigi}")
    print(f"\n✅ İşlenmiş veriler '{output_path}' konumuna kaydedildi.")

if __name__ == "__main__":
    process_pipeline()