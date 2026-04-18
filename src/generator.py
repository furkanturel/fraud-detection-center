import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid
import os

fake = Faker('tr_TR')

DATA_DIR = "../data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_advanced_data(num_users=1000, num_normal_txn=15000):
    print("🏦 Banka Standartlarında Gelişmiş Veri Üreticisi Başlatılıyor...")
    
    # 1. KULLANICILAR (Müşteriler)
    users = []
    cities = ['İstanbul', 'Ankara', 'İzmir', 'Antalya', 'Bursa', 'Adana', 'Sakarya', 'Trabzon', 'Konya', 'Kayseri']
    
    for _ in range(num_users):
        users.append({
            "user_id": f"U_{fake.uuid4()[:8]}",
            "name": fake.name(),
            "age": random.randint(18, 80),
            "home_city": random.choice(cities),
            "account_balance": round(random.uniform(1000, 50000), 2)
        })
    df_users = pd.DataFrame(users)
    
    # 2. İŞYERLERİ (Merchants)
    merchants = []
    categories = ['Market', 'Akaryakıt', 'Kafe/Restoran', 'Giyim', 'Elektronik', 'Kuyumcu', 'Kripto/Finans']
    
    for _ in range(200):
        merchants.append({
            "merchant_id": f"M_{fake.uuid4()[:8]}",
            "merchant_name": fake.company(),
            "category": random.choice(categories),
            "merchant_city": random.choice(cities)
        })
    df_merchants = pd.DataFrame(merchants)
    
    # 3. İŞLEMLER (Transactions)
    transactions = []
    user_ids = df_users['user_id'].tolist()
    merchant_ids = df_merchants['merchant_id'].tolist()
    
    print("✅ Temiz işlemler üretiliyor...")
    base_time = datetime.now() - timedelta(days=30)
    
    for _ in range(num_normal_txn):
        txn_time = base_time + timedelta(minutes=random.randint(1, 43200)) # Son 30 gün
        if txn_time.hour < 6 and random.random() > 0.1: # Geceleri normal işlem az olur
            txn_time = txn_time.replace(hour=random.randint(8, 22))
            
        transactions.append({
            "transaction_id": f"T_{fake.uuid4()[:12]}",
            "user_id": random.choice(user_ids),
            "merchant_id": random.choice(merchant_ids),
            "amount": round(random.uniform(5.0, 1500.0), 2),
            "transaction_date": txn_time,
            "is_fraud": 0,
            "scenario": "Normal"
        })

    # --- SİHRİN BAŞLADIĞI YER: SENARYO ENJEKSİYONU ---
    print("🚨 Kural İhlalleri (Fraud Senaryoları) veriye gizleniyor...")

    # Senaryo 1: İmkansız Konum (Location Jump)
    for _ in range(50):
        victim = random.choice(user_ids)
        m1 = df_merchants[df_merchants['merchant_city'] == 'İstanbul'].sample(1).iloc[0]['merchant_id']
        m2 = df_merchants[df_merchants['merchant_city'] == 'Antalya'].sample(1).iloc[0]['merchant_id']
        t_time = base_time + timedelta(days=random.randint(1, 28))
        
        transactions.append({"transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m1, "amount": 150.0, "transaction_date": t_time, "is_fraud": 0, "scenario": "Normal"})
        # Sadece 15 dk sonra Antalya'da işlem!
        transactions.append({"transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m2, "amount": 4500.0, "transaction_date": t_time + timedelta(minutes=15), "is_fraud": 1, "scenario": "Location_Jump"})

    # Senaryo 2: Hız İhlali (Velocity - Seri Çekim)
    for _ in range(40):
        victim = random.choice(user_ids)
        m_evil = df_merchants[df_merchants['category'] == 'Elektronik'].sample(1).iloc[0]['merchant_id']
        t_time = base_time + timedelta(days=random.randint(1, 28))
        
        # 5 dakika içinde 6 işlem
        for i in range(6):
            transactions.append({
                "transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m_evil,
                "amount": round(random.uniform(2000, 4000), 2),
                "transaction_date": t_time + timedelta(seconds=i*45), # 45 saniyede bir
                "is_fraud": 1, "scenario": "Velocity_Spike"
            })

    # Senaryo 3: Mikro Test & Büyük Vurgun (Card Testing)
    for _ in range(60):
        victim = random.choice(user_ids)
        m_evil = random.choice(merchant_ids)
        t_time = base_time + timedelta(days=random.randint(1, 28))
        
        transactions.append({"transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m_evil, "amount": 1.00, "transaction_date": t_time, "is_fraud": 1, "scenario": "Card_Testing"})
        transactions.append({"transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m_evil, "amount": 2.50, "transaction_date": t_time + timedelta(minutes=2), "is_fraud": 1, "scenario": "Card_Testing"})
        transactions.append({"transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m_evil, "amount": 15000.00, "transaction_date": t_time + timedelta(minutes=5), "is_fraud": 1, "scenario": "Card_Testing"})

    # Senaryo 4: Gece Yarısı Tam Sayı (Midnight Round Amount)
    for _ in range(70):
        victim = random.choice(user_ids)
        m_evil = df_merchants[df_merchants['category'].isin(['Kuyumcu', 'Kripto/Finans'])].sample(1).iloc[0]['merchant_id']
        t_time = base_time + timedelta(days=random.randint(1, 28))
        t_time = t_time.replace(hour=random.randint(2, 4)) # Gece 2 ile 4 arası
        
        transactions.append({
            "transaction_id": str(uuid.uuid4()), "user_id": victim, "merchant_id": m_evil,
            "amount": float(random.choice([5000, 10000, 25000, 50000])), # Küsüratsız tam sayılar
            "transaction_date": t_time,
            "is_fraud": 1, "scenario": "Midnight_Round_Amount"
        })

    # Verileri karıştır (zamana göre sıralı olmasın)
    df_txn = pd.DataFrame(transactions).sample(frac=1).reset_index(drop=True)
    
    # CSV'ye kaydet
    df_users.to_csv(f"{DATA_DIR}/users.csv", index=False)
    df_merchants.to_csv(f"{DATA_DIR}/merchants.csv", index=False)
    df_txn.to_csv(f"{DATA_DIR}/transactions.csv", index=False)
    
    print("\n📊 İŞLEM TAMAMLANDI!")
    print(f"Toplam Kullanıcı: {len(df_users)}")
    print(f"Toplam İşyeri: {len(df_merchants)}")
    print(f"Toplam İşlem: {len(df_txn)} (İçinde yüzlerce gizli fraud kural ihlali var)")

if __name__ == "__main__":
    generate_advanced_data()