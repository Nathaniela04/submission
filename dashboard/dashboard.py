import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# COLOR PALETTE
PRIMARY = '#4e79a7'
SECONDARY = '#d3d3d3'
ACCENT = '#1e3a5f'
HIGHLIGHT = '#cdb4db' 

#PAGE CONFIG
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

#STYLING
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
    }
    .stMetric { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


#LOAD DATA
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    if 'temp' in df.columns and 'temp_celsius' not in df.columns:
        df['temp_celsius'] = df['temp'] * 41
    return df


@st.cache_data
def load_hour():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    hour_path = os.path.join(BASE_DIR, "..", "data", "hour.csv")
    hdf = pd.read_csv(hour_path) if os.path.exists(hour_path) else None
    if hdf is None:
        return None
    hdf['dteday'] = pd.to_datetime(hdf['dteday'])
    return hdf


day_df = load_data()
hour_df = load_hour()

#SIDEBAR
with st.sidebar:
    st.title("🚴🏻 Bike Sharing")
    st.divider()

    # Date Range
    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    date_range = st.date_input(
        "Filter Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Season
    season_options = ['Semua'] + sorted(day_df['season_label'].unique().tolist())
    selected_season = st.selectbox("Musim", season_options)

    # Weather
    weather_options = ['Semua'] + sorted(day_df['weather_label'].unique().tolist())
    selected_weather = st.selectbox("Cuaca", weather_options)

    st.divider()

#FILTER DATA
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = day_df[
        (day_df['dteday'].dt.date >= start_date) &
        (day_df['dteday'].dt.date <= end_date)
    ]
else:
    filtered = day_df.copy()

if selected_season != 'Semua':
    filtered = filtered[filtered['season_label'] == selected_season]
if selected_weather != 'Semua':
    filtered = filtered[filtered['weather_label'] == selected_weather]

#HEADER
st.markdown('<p class="main-title">Bike Sharing Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Analisis Pola Peminjaman Sepeda</p>', unsafe_allow_html=True)

#KPI METRICS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Peminjaman", f"{filtered['cnt'].sum():,.0f}", 
            delta=f"{filtered['cnt'].sum() - day_df['cnt'].sum()//2:,.0f} vs setengah data")
col2.metric("Rata-rata Harian", f"{filtered['cnt'].mean():,.0f}")
col3.metric("Maksimum", f"{filtered['cnt'].max():,.0f}")
col4.metric("Jumlah Hari", f"{len(filtered):,}")

st.divider()

#SECTION 1: TREN HARIAN
st.subheader("Tren Peminjaman Sepeda Harian")

fig, ax = plt.subplots(figsize=(12, 4))
ax.fill_between(filtered['dteday'], filtered['cnt'], alpha=0.15, color=PRIMARY)
ax.plot(filtered['dteday'], filtered['cnt'], color=PRIMARY, linewidth=1.2)
# 30-day rolling average
if len(filtered) > 30:
    rolling = filtered.set_index('dteday')['cnt'].rolling(30).mean()
    ax.plot(rolling.index, rolling.values, color='#e63946', linewidth=2, 
            linestyle='--', label='Rata-rata 30 hari')
    ax.legend(fontsize=9)
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Peminjaman")
ax.set_title("")
sns.despine()
plt.tight_layout()
st.pyplot(fig)
plt.close()

#SECTION 2: MUSIM & CUACA (Pertanyaan Bisnis 1)
st.divider()
st.subheader("Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Peminjaman")

col_a, col_b = st.columns(2)

with col_a:
    season_agg = filtered.groupby('season_label')['cnt'].mean()
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    season_agg = season_agg.reindex([s for s in season_order if s in season_agg.index])

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [SECONDARY, SECONDARY, PRIMARY, SECONDARY][:len(season_agg)]
    bars = ax.bar(season_agg.index, season_agg.values, color=colors, edgecolor='white', linewidth=1.5)
    ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=9)
    ax.set_title('Rata-rata Peminjaman per Musim', fontweight='bold')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.set_ylim(0, season_agg.max() * 1.15 if len(season_agg) > 0 else 1)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_b:
    weather_agg = filtered.groupby('weather_label')['cnt'].mean()
    weather_order = ['Clear', 'Mist/Cloudy', 'Light Rain/Snow', 'Heavy Rain/Snow']
    weather_agg = weather_agg.reindex([w for w in weather_order if w in weather_agg.index])

    fig, ax = plt.subplots(figsize=(6, 4))
    colors_w = [PRIMARY, SECONDARY, SECONDARY, SECONDARY][:len(weather_agg)]
    bars2 = ax.bar(weather_agg.index, weather_agg.values, color=colors_w, edgecolor='white', linewidth=1.5)
    ax.bar_label(bars2, fmt='%.0f', padding=3, fontsize=9)
    ax.set_title('Rata-rata Peminjaman per Kondisi Cuaca', fontweight='bold')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.set_ylim(0, weather_agg.max() * 1.15 if len(weather_agg) > 0 else 1)
    ax.tick_params(axis='x', rotation=15)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with st.expander("Insight Pertanyaan 1"):
    st.markdown("""
    - **Fall (Musim Gugur)** secara konsisten memiliki rata-rata peminjaman tertinggi (~5.644/hari), 
      diikuti Summer, Winter, dan Spring.
    - **Cuaca cerah** menghasilkan peminjaman **~2–3× lebih banyak** dibanding kondisi hujan/salju.
    - **Rekomendasi**: Operator harus meningkatkan ketersediaan armada di musim gugur dan mempersiapkan 
      strategi insentif (diskon) pada hari cuaca buruk untuk menjaga volume peminjaman.
    """)

#SECTION 3: POLA PER JAM (Pertanyaan Bisnis 2)
st.divider()
st.subheader("Pertanyaan 2: Pola Peminjaman per Jam (Hari Kerja vs Hari Libur)")

if hour_df is not None:
    filtered_hour = hour_df.copy()
    if len(date_range) == 2:
        filtered_hour = filtered_hour[
            (pd.to_datetime(filtered_hour['dteday']).dt.date >= start_date) &
            (pd.to_datetime(filtered_hour['dteday']).dt.date <= end_date)
        ]
    if selected_season != 'Semua':
        season_map = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
        if selected_season in season_map:
            filtered_hour = filtered_hour[filtered_hour['season'] == season_map[selected_season]]
    if selected_weather != 'Semua':
        weather_map = {'Clear': 1, 'Mist/Cloudy': 2, 'Light Rain/Snow': 3, 'Heavy Rain/Snow': 4}
        if selected_weather in weather_map:
            filtered_hour = filtered_hour[filtered_hour['weathersit'] == weather_map[selected_weather]]
    hourly = filtered_hour.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()
    work = hourly[hourly['workingday'] == 1]
    non_work = hourly[hourly['workingday'] == 0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4), sharey=True)

    #Working day
    axes[0].fill_between(work['hr'], work['cnt'], alpha=0.2, color=PRIMARY)
    axes[0].plot(work['hr'], work['cnt'], color=ACCENT, linewidth=2.5, marker='o', markersize=3)
    axes[0].axvline(x=8, color='red', linestyle='--', alpha=0.7, label='Jam 8 (Puncak pagi)')
    axes[0].axvline(x=17, color='orange', linestyle='--', alpha=0.7, label='Jam 17 (Puncak sore)')
    axes[0].set_title('Hari Kerja', fontweight='bold', color='#1565C0')
    axes[0].set_xlabel('Jam')
    axes[0].set_ylabel('Rata-rata Peminjaman')
    axes[0].set_xticks(range(0, 24, 2))
    axes[0].legend(fontsize=8)
    sns.despine(ax=axes[0])

    #Non-working day
    axes[1].fill_between(non_work['hr'], non_work['cnt'], alpha=0.2, color=SECONDARY)
    axes[1].plot(non_work['hr'], non_work['cnt'], color=ACCENT, linewidth=2.5, marker='o', markersize=3)
    axes[1].axvline(x=13, color='purple', linestyle='--', alpha=0.7, label='Jam 13 (Puncak siang)')
    axes[1].set_title('Hari Libur / Weekend', fontweight='bold', color='#2E7D32')
    axes[1].set_xlabel('Jam')
    axes[1].set_xticks(range(0, 24, 2))
    axes[1].legend(fontsize=8)
    sns.despine(ax=axes[1])

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    with st.expander("Insight Pertanyaan 2"):
        st.markdown("""
        - **Hari kerja** menunjukkan pola **bimodal**: puncak jam **08:00** (berangkat kerja) dan **17:00–18:00** (pulang kerja).
        - **Hari libur/weekend** menunjukkan pola **unimodal**: naik perlahan dari pagi, puncak jam **12:00–14:00** (rekreasi).
        - **Rekomendasi**: 
          - Hari kerja → distribusikan sepeda ke stasiun/perkantoran jam 7–9 dan 16–18.
          - Hari libur → perkuat distribusi di taman & area wisata siang hari.
        """)
else:
    st.info("Data per jam (hour.csv) tidak tersedia di folder ini. Letakkan hour.csv di folder `data/`.")

#SECTION 4: CLUSTERING
st.divider()
st.subheader("Analisis Lanjutan: Clustering Permintaan (Manual Binning)")

bins = [0, 2000, 4000, 6000, day_df['cnt'].max() + 1]  
labels = ['Low\n(0–2K)', 'Moderate\n(2K–4K)', 'High\n(4K–6K)', 'Very High\n(>6K)']
filtered = filtered.copy()
filtered['demand_category'] = pd.cut(filtered['cnt'], bins=bins, labels=labels)

col1, col2 = st.columns(2)

with col1:
    counts = filtered['demand_category'].value_counts().reindex(labels)
    fig, ax = plt.subplots(figsize=(6, 4))
    cluster_colors = [SECONDARY, SECONDARY, PRIMARY, SECONDARY]
    bars = ax.bar(labels, counts.values, color=cluster_colors, edgecolor='white', linewidth=1.5)
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_title('Distribusi Hari per Kategori Permintaan', fontweight='bold')
    ax.set_ylabel('Jumlah Hari')
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    avg_temp = filtered.groupby('demand_category')['temp_celsius'].mean().reindex(labels)
    fig, ax = plt.subplots(figsize=(6, 4))
    cluster_colors2 = [SECONDARY, SECONDARY, SECONDARY, PRIMARY]
    bars2 = ax.bar(labels, avg_temp.values, color=cluster_colors2, edgecolor='white', linewidth=1.5)
    ax.bar_label(bars2, fmt='%.1f°C', padding=3, fontsize=9)
    ax.set_title('Rata-rata Suhu per Kategori Permintaan', fontweight='bold')
    ax.set_ylabel('Suhu (°C)')
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("**Tabel Profil Cluster:**")
profile = filtered.groupby('demand_category').agg(
    Jumlah_Hari=('cnt', 'count'),
    Avg_Peminjaman=('cnt', 'mean'),
    Avg_Suhu_C=('temp_celsius', 'mean'),
    Avg_Kelembaban=('hum', lambda x: x.mean() * 100),
    Pct_Hari_Kerja=('workingday', lambda x: x.mean() * 100),
    Pct_Cuaca_Cerah=('weathersit', lambda x: (x == 1).mean() * 100)
).round(1).reindex(labels)
st.dataframe(profile, use_container_width=True)

#FOOTER
st.divider()
st.caption("Dashboard dibuat menggunakan Streamlit · Dataset: Capital Bikeshare, Nathaniela Isya-")
