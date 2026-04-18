import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="FraudGuard SOC Commander", page_icon="🛡️", layout="wide")

# --- 2. SABİT KARANLIK TEMA RENKLERİ ---
BG_COLOR = "#0e1117"
CARD_BG = "#1c2128"
TEXT_COLOR = "#ffffff"
BORDER_COLOR = "#30363d"
PLOT_TEMPLATE = "plotly_dark"
GRID_COLOR = "#30363d"
SUB_TEXT = "#adb5bd"
COLORS = ["#236b62", "#3a9679", "#f18f67", "#84c4b4", "#f2c695"]
DARK_GREEN = "#1e5b53"

# --- 3. CSS (SABİT DARK MODE TASARIMI) ---
st.markdown(f"""
    <style>
    /* Ana Ekran ve Sidebar */
    .stApp {{ background-color: {BG_COLOR} !important; }}
    [data-testid="stSidebar"] {{ 
        background-color: {CARD_BG} !important; 
        border-right: 1px solid {BORDER_COLOR}; 
    }}

    /* Tüm Yazılar Beyaz */
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown, div {{ 
        color: {TEXT_COLOR} !important; 
    }}
    
    /* Metrik Kartları */
    .op-card {{
        background-color: {CARD_BG};
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border: 1px solid {BORDER_COLOR};
        margin-bottom: 20px;
    }}
    .special-card {{
        background-color: {DARK_GREEN} !important;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .special-card h2, .special-card h4 {{ color: white !important; margin: 0; }}
    
    /* Dosya Yükleyici */
    [data-testid="stFileUploader"] {{
        background-color: {BG_COLOR} !important;
        border: 1px dashed {BORDER_COLOR} !important;
    }}
    
    /* Input ve Tablolar */
    .stTextInput>div>div>input {{ 
        background-color: {BG_COLOR}; 
        color: white; 
        border: 1px solid {BORDER_COLOR}; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ MOTORU ---
def process_dynamic_csv(df):
    df = df.copy()
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['hour'] = df['transaction_date'].dt.hour
    df['risk_score'] = 0
    df['scenario'] = "Normal"
    if 'amount' in df.columns:
        df.loc[df['amount'] > 12000, 'risk_score'] += 40
        df.loc[df['amount'] > 12000, 'scenario'] = "High_Amount"
    df['system_decision'] = df['risk_score'].apply(lambda x: 'FRAUD_ENGEL' if x >= 40 else 'ONAYLANDI')
    return df

@st.cache_data
def load_db_data():
    try:
        conn = sqlite3.connect("../data/fraud_warehouse.db")
        query = "SELECT f.*, u.name, m.merchant_name, m.category, m.merchant_city, d.full_date, d.hour FROM fact_transactions f JOIN dim_users u ON f.user_id = u.user_id JOIN dim_merchants m ON f.merchant_id = m.merchant_id JOIN dim_date d ON f.date_id = d.date_id"
        df = pd.read_sql(query, conn)
        df['full_date'] = pd.to_datetime(df['full_date'])
        conn.close()
        return df
    except: return pd.DataFrame()

# Sidebar İçeriği
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>FraudGuard</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### Veri Kaynağı")
    uploaded_file = st.file_uploader("Yeni CSV Yükle", type=["csv"])
    st.divider()

# Veri Seçimi
if uploaded_file is not None:
    df = process_dynamic_csv(pd.read_csv(uploaded_file))
else:
    df = load_db_data()

if not df.empty:
    with st.sidebar:
        st.markdown("### Filtreler")
        risk_val = st.slider("Min Risk Skoru", 0, 100, 20)
        st.divider()
        st.markdown("### Sektörler")
        all_cats = sorted(df['category'].unique()) if 'category' in df.columns else []
        sel_all = st.toggle("Hepsini Seç", value=True)
        selected_cats = [c for c in all_cats if st.checkbox(c, value=sel_all)]

    filtered_df = df[(df['risk_score'] >= risk_val)]
    if 'category' in df.columns:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_cats)]
    fraud_df = filtered_df[filtered_df['system_decision'] == 'FRAUD_ENGEL']

    # --- 5. ANA EKRAN ---
    st.markdown(f"<h1 style='text-align: center;'> FraudGuard</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([" Yönetici Özeti", " Risk Analizi", " Akıllı Veri Gezgini"])

    # TAB 1: ÖZET
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="op-card"><h4>İşlem Hacmi</h4><h2>{len(filtered_df):,}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="op-card"><h4>Bloke Edilen</h4><h2 style="color:#e74c3c !important;">{len(fraud_df):,}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="op-card"><h4>Ortalama Risk</h4><h2>%{filtered_df["risk_score"].mean():.1f}</h2></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="special-card"><h4>Kurtarılan Tutar</h4><h2>₺{fraud_df["amount"].sum():,.0f}</h2></div>', unsafe_allow_html=True)

        cl, cr = st.columns(2)
        with cl:
            fig_bar = px.bar(fraud_df.groupby('category').size().reset_index(name='v'), x='category', y='v', color_discrete_sequence=[COLORS[0]], template=PLOT_TEMPLATE, title="Sektörel Risk")
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        with cr:
            fig_pie = px.pie(fraud_df, names='scenario', hole=0.5, color_discrete_sequence=COLORS, template=PLOT_TEMPLATE, title="Senaryo Analizi")
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

    # TAB 2: RİSK ANALİZİ
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="op-card">', unsafe_allow_html=True)
        st.markdown(f"<h4> Fraud Zaman Analizi</h4>", unsafe_allow_html=True)
        if 'hour' in fraud_df.columns:
            hourly_fraud = fraud_df.groupby('hour').size().reset_index(name='v')
            fig_heat = px.line(hourly_fraud, x='hour', y='v', markers=True, color_discrete_sequence=[COLORS[2]], template=PLOT_TEMPLATE)
            fig_heat.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig_heat.update_xaxes(title="Günlük Saatler", gridcolor=GRID_COLOR)
            fig_heat.update_yaxes(title="Vaka Sayısı", gridcolor=GRID_COLOR)
            st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        clow, crig = st.columns([7, 3])
        with clow:
            st.markdown(f'<div class="op-card"><h4> Risk Matrisi (Tutar & Skor)</h4>', unsafe_allow_html=True)
            fig_mat = px.scatter(fraud_df.head(150), x="risk_score", y="amount", size="amount", color="scenario", color_discrete_sequence=COLORS, template=PLOT_TEMPLATE)
            fig_mat.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_mat, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with crig:
            st.markdown(f'<div class="op-card" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown(f"<h4>Genel Tehdit</h4>", unsafe_allow_html=True)
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=fraud_df['risk_score'].mean() if not fraud_df.empty else 0, number={'suffix': "%", 'font':{'color':TEXT_COLOR}},
                    gauge={'axis':{'range':[None, 100], 'visible':False}, 'bar':{'color':COLORS[0]}, 'steps':[{'range':[0,75],'color':COLORS[3]},{'range':[75,100],'color':COLORS[2]}]}))
            fig_g.update_layout(height=180, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
            st.markdown(f"<h2 style='color:#e74c3c !important;'>{len(fraud_df)}</h2><span>Kritik Vaka</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3: VERİ GEZGİNİ
    with tab3:
        st.markdown("### Sorgu Paneli")
        search = st.text_input(" Müşteri veya İşyeri Ara...")
        display_df = filtered_df
        if search:
            mask = filtered_df['name'].str.contains(search, case=False, na=False) if 'name' in filtered_df.columns else False
            mask |= filtered_df['merchant_name'].str.contains(search, case=False, na=False) if 'merchant_name' in filtered_df.columns else False
            display_df = filtered_df[mask]
        
        st.dataframe(
            display_df.sort_values(by='risk_score', ascending=False),
            column_config={
                "amount": st.column_config.NumberColumn("Tutar", format="₺ %.2f"),
                "risk_score": st.column_config.ProgressColumn("Risk", min_value=0, max_value=100, format="%d"),
                "full_date": "Tarih",
                "name": "Müşteri"
            },
            use_container_width=True, hide_index=True
        )
else:
    st.warning("⚠️ Lütfen veritabanını oluşturun veya bir CSV yükleyin.")