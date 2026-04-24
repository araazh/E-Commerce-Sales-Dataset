import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from babel.numbers import format_number

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.section-header {
    font-size: 20px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
}
.insight-box {
    padding: 12px;
    border-left: 4px solid #3B82F6;
    border-radius: 6px;
    background-color: rgba(59,130,246,0.08);
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")

    datetime_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "actual_delivery_time" not in df.columns:
        df["actual_delivery_time"] = (
            df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
        ).dt.days
    if "delivery_vs_estimated" not in df.columns:
        df["delivery_vs_estimated"] = (
            df["order_estimated_delivery_date"] - df["order_delivered_customer_date"]
        ).dt.days

    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## E-Commerce Dashboard")
    st.markdown("---")

    st.markdown("### 🗓️ Filter Periode")
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()

    start_date = st.date_input("Dari", value=min_date, min_value=min_date, max_value=max_date)
    end_date   = st.date_input("Sampai", value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("### 📥 Filter Status Pesanan")
    all_status = df["order_status"].dropna().unique().tolist()
    selected_status = st.multiselect("Status", all_status, default=["delivered"])

    st.markdown("### 🌏 Filter Negara Bagian")
    all_states = sorted(df["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect("Negara Bagian", all_states, default=all_states)

    st.markdown("### 📝 Jumlah Kategori Ditampilkan")
    top_n = st.slider("Top N kategori", min_value=5, max_value=20, value=10)

    st.markdown("---")
    st.caption("Dibuat Oleh: Azzahra Fitri Ramadhanti")

    st.markdown("---")
    st.caption("Data: Brazilian E-Commerce Public Dataset · 2016–2018")

# ── Filter dataframe ──────────────────────────────────────────────────────────
mask = (
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["order_status"].isin(selected_status)) &
    (df["customer_state"].isin(selected_states))
)
filtered_df = df[mask].copy()

# ── Helper: styled figure ────────────────────────────────────────────────────
def styled_fig(figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#E8EAF0")
    ax.tick_params(colors="#6B7280", labelsize=10)
    ax.xaxis.label.set_color("#374151")
    ax.yaxis.label.set_color("#374151")
    ax.title.set_color("#111827")
    return fig, ax

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🛍️ E-Commerce — Dashboard Analisis")
st.markdown(
    f"Menampilkan data **{start_date}** s/d **{end_date}** · "
    f"Status: **{', '.join(selected_status)}** · "
    f"{len(selected_states)} negara bagian dipilih"
)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# METRIK UTAMA
# ══════════════════════════════════════════════════════════════════════════════
total_orders    = filtered_df["order_id"].nunique()
total_customers = filtered_df["customer_unique_id"].nunique() if "customer_unique_id" in filtered_df.columns else 0
avg_review      = filtered_df["review_score"].mean() if "review_score" in filtered_df.columns else 0
avg_delivery    = filtered_df["actual_delivery_time"].mean() if "actual_delivery_time" in filtered_df.columns else 0
total_revenue = (
    filtered_df.drop_duplicates(subset='order_id')['total_payment_value'].sum()
    if 'total_payment_value' in filtered_df.columns else 0
)
def format_revenue(value):
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"R$ {value/1_000:.1f}K"
    else:
        return f"R$ {value:.0f}"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Pesanan", f"{total_orders:,}", "order unik")
with col2:
    st.metric("Total Pelanggan", f"{total_customers:,}", "customer unik")
with col3:
    st.metric("Total Revenue", format_revenue(total_revenue), "nilai pendapatan")
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB NAVIGASI
# ════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Kategori Produk",
    "⛟ Statistik Pengiriman",
    "👥 Segmentasi Pelanggan (RFM)",
    "📈 Tren Penjualan"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KATEGORI PRODUK
# ══════════════════════════════════
with tab1:
    st.subheader("Performa Kategori Produk")

    # Agregasi
    if "product_category_name_english" in filtered_df.columns:
        cat_df = (
            filtered_df
            .groupby("product_category_name_english")
            .agg(
                total_items_sold=("order_item_id", "count"),
                avg_review_score=("review_score", "mean")
            )
            .reset_index()
            .sort_values("total_items_sold", ascending=False)
        )
        top_cat  = cat_df.head(top_n)
        top_rev  = cat_df.sort_values("avg_review_score", ascending=False).head(top_n)
        bot_rev  = cat_df.sort_values("avg_review_score", ascending=True).head(top_n)

        # ── Row 1: popularitas + review top kategori ──────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"**Top {top_n} Kategori | Jumlah Item Terjual**")
            fig, ax = styled_fig((8, top_n * 0.45 + 1))
            colors = sns.color_palette("Blues_r", top_n)
            bars = ax.barh(
                top_cat["product_category_name_english"][::-1],
                top_cat["total_items_sold"][::-1],
                color=colors, edgecolor="none", height=0.65
            )
            for bar, val in zip(bars, top_cat["total_items_sold"][::-1]):
                ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                        f"{val:,}", va="center", fontsize=9, color="#6B7280")
            ax.set_xlabel("Jumlah Item Terjual")
            ax.set_ylabel("")
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()

        with c2:
            st.markdown(f"**Top {top_n} Kategori | Rata-rata Skor Ulasan**")
            fig, ax = styled_fig((8, top_n * 0.45 + 1))
            palette = sns.color_palette("RdYlGn", top_n)
            sorted_rev = top_cat.sort_values("avg_review_score", ascending=True)
            ax.barh(
                sorted_rev["product_category_name_english"],
                sorted_rev["avg_review_score"],
                color=palette, edgecolor="none", height=0.65
            )
            ax.axvline(top_cat["avg_review_score"].mean(), color="#3B82F6",
                       linestyle="--", linewidth=1.2,
                       label=f"Rata-rata: {top_cat['avg_review_score'].mean():.2f}")
            ax.set_xlabel("Rata-rata Skor Ulasan (1–5)")
            ax.set_ylabel("")
            ax.set_xlim(0, 5)
            ax.legend(fontsize=9)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 2: top & bottom review score keseluruhan ──────────────────────
        c3, c4 = st.columns(2)

        with c3:
            st.markdown("**Top 10 Kategori | Skor Ulasan Tertinggi (seluruh kategori)**")
            fig, ax = styled_fig((8, 5))
            sns.barplot(ax=ax, x="avg_review_score", y="product_category_name_english",
                        data=top_rev, palette="Greens_r", legend=False)
            ax.set_xlim(3.5, 5)
            ax.set_xlabel("Rata-rata Skor Ulasan")
            ax.set_ylabel("")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()

        with c4:
            st.markdown("**Bottom 10 Kategori | Skor Ulasan Terendah (seluruh kategori)**")
            fig, ax = styled_fig((8, 5))
            sns.barplot(ax=ax, x="avg_review_score", y="product_category_name_english",
                        data=bot_rev, palette="Reds_r", legend=False)
            ax.set_xlim(0, 3.5)
            ax.set_xlabel("Rata-rata Skor Ulasan")
            ax.set_ylabel("")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
    else:
        st.warning("Kolom `product_category_name_english` tidak ditemukan di data.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EFISIENSI PENGIRIMAN
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(" Statistik Pengiriman")

    delivery_df = filtered_df[
        (filtered_df["actual_delivery_time"].notna()) &
        (filtered_df["delivery_vs_estimated"].notna()) &
        (filtered_df["actual_delivery_time"] > 0)
    ].copy()

    if delivery_df.empty:
        st.warning("Tidak ada data pengiriman untuk filter yang dipilih.")
    else:
        # Metrik pengiriman
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Rata-rata Pengiriman",
                    f"{delivery_df['actual_delivery_time'].mean():.1f} hari")
        with m2:
            st.metric("Rata-rata vs Estimasi",
                    f"+{delivery_df['delivery_vs_estimated'].mean():.1f} hari",
                    "positif = lebih cepat")
        with m3:
            pct_late = (delivery_df["delivery_vs_estimated"] < 0).mean() * 100
            st.metric("Pesanan Terlambat", f"{pct_late:.1f}%")
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 1: distribusi ─────────────────────────────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Distribusi Waktu Pengiriman Aktual (Hari)**")
            fig, ax = styled_fig((8, 4))
            ax.hist(delivery_df["actual_delivery_time"].dropna(),
                    bins=40, color="#3B82F6", edgecolor="none", alpha=0.85)
            mean_val = delivery_df["actual_delivery_time"].mean()
            ax.axvline(mean_val, color="#EF4444", linestyle="--", linewidth=1.5,
                       label=f"Mean: {mean_val:.1f} hari")
            ax.set_xlabel("Waktu Pengiriman (Hari)")
            ax.set_ylabel("Jumlah Pesanan")
            ax.legend(fontsize=9)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()

        with c2:
            st.markdown("**Distribusi Selisih Pengiriman vs Estimasi**")
            fig, ax = styled_fig((8, 4))
            data_plot = delivery_df["delivery_vs_estimated"].dropna()
            colors_hist = ["#EF4444" if x < 0 else "#22C55E" for x in data_plot]
            ax.hist(data_plot, bins=40, color="#10B981", edgecolor="none", alpha=0.75)
            ax.axvline(0, color="#111827", linestyle="--", linewidth=1.2, label="Tepat estimasi")
            mean_ve = data_plot.mean()
            ax.axvline(mean_ve, color="#F59E0B", linestyle="--", linewidth=1.5,
                       label=f"Mean: +{mean_ve:.1f} hari")
            ax.set_xlabel("Selisih (Hari) — Positif = Lebih Cepat")
            ax.set_ylabel("Jumlah Pesanan")
            ax.legend(fontsize=9)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 2: per wilayah ────────────────────────────────────────────────
        if "customer_state" in delivery_df.columns:
            state_df = (
                delivery_df
                .groupby("customer_state")
                .agg(
                    mean_actual=("actual_delivery_time", "mean"),
                    mean_vs_est=("delivery_vs_estimated", "mean"),
                    total_orders=("order_id", "nunique")
                )
                .reset_index()
            )

            c3, c4 = st.columns(2)

            with c3:
                st.markdown("**Top 10 Negara Bagian | Pengiriman Terlama**")
                slowest = state_df.sort_values("mean_actual", ascending=False).head(10)
                fig, ax = styled_fig((8, 5))
                palette = sns.color_palette("YlOrRd", 10)
                sns.barplot(ax=ax, x="mean_actual", y="customer_state",
                            data=slowest, palette=palette[::-1], legend=False)
                ax.set_xlabel("Rata-rata Waktu Pengiriman (Hari)")
                ax.set_ylabel("Negara Bagian")
                fig.tight_layout()
                st.pyplot(fig)
                plt.close()

            with c4:
                st.markdown("**Top 10 Negara Bagian | Paling Sering Melewati Estimasi**")
                latest = state_df.sort_values("mean_vs_est", ascending=True).head(10)
                fig, ax = styled_fig((8, 5))
                colors_late = ["#EF4444" if v < 0 else "#22C55E"
                               for v in latest["mean_vs_est"]]
                ax.barh(latest["customer_state"], latest["mean_vs_est"],
                        color=colors_late, edgecolor="none", height=0.65)
                ax.axvline(0, color="#111827", linestyle="--", linewidth=1, alpha=0.5)
                ax.set_xlabel("Selisih vs Estimasi (Hari) — Merah = Terlambat")
                ax.set_ylabel("Negara Bagian")
                fig.tight_layout()
                st.pyplot(fig)
                plt.close()
            # ── Tabel ringkasan per state ─────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Ringkasan Efisiensi Pengiriman per Negara Bagian**")
            display_state = state_df.sort_values("mean_actual", ascending=False).copy()
            display_state.columns = [
                "Negara Bagian", "Rata-rata Pengiriman (Hari)",
                "Rata-rata vs Estimasi (Hari)", "Total Pesanan"
            ]
            display_state["Rata-rata Pengiriman (Hari)"] = display_state["Rata-rata Pengiriman (Hari)"].round(1)
            display_state["Rata-rata vs Estimasi (Hari)"] = display_state["Rata-rata vs Estimasi (Hari)"].round(1)
            st.dataframe(display_state, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RFM SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Analisis Lanjutan: Segmentasi Pelanggan Berdasarkan RFM</div>', unsafe_allow_html=True)

    if "Customer_Segment" in filtered_df.columns:
        seg_df = (
            filtered_df
            .drop_duplicates(subset=["customer_unique_id"])
            [["customer_unique_id", "Recency", "Frequency", "Monetary", "Customer_Segment"]]
            .dropna(subset=["Customer_Segment"])
        )

        seg_counts = seg_df["Customer_Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segmen", "Jumlah"]

        seg_colors = {
            "Pelanggan Setia":       "#22C55E",
            "Pelanggan Potensial":   "#3B82F6",
            "Pelanggan Baru":        "#F59E0B",
            "Pelanggan Tidak Aktif": "#EF4444",
        }

        c1, c2 = st.columns([1.2, 1])

        with c1:
            st.markdown("**Distribusi Segmen Pelanggan**")
            fig, ax = styled_fig((8, 5))
            colors_seg = [seg_colors.get(s, "#9CA3AF") for s in seg_counts["Segmen"]]
            bars = ax.bar(seg_counts["Segmen"], seg_counts["Jumlah"],
                          color=colors_seg, edgecolor="none", width=0.55)
            for bar, val in zip(bars, seg_counts["Jumlah"]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                        f"{val:,}", ha="center", fontsize=10, color="#374151")
            ax.set_xlabel("Segmen Pelanggan")
            ax.set_ylabel("Jumlah Pelanggan")
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()

        with c2:
            st.markdown("**Proporsi Segmen**")
            fig, ax = plt.subplots(figsize=(6, 5))
            fig.patch.set_facecolor("#FFFFFF")
            colors_pie = [seg_colors.get(s, "#9CA3AF") for s in seg_counts["Segmen"]]
            wedges, texts, autotexts = ax.pie(
                seg_counts["Jumlah"],
                labels=seg_counts["Segmen"],
                colors=colors_pie,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2}
            )
            for t in texts:
                t.set_fontsize(10)
                t.set_color("#374151")
            for at in autotexts:
                at.set_fontsize(9)
                at.set_color("white")
                at.set_fontweight("bold")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()

        # ── RFM metrics per segment ───────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Rata-rata Nilai RFM per Segmen**")
        rfm_summary = (
            seg_df.groupby("Customer_Segment")
            .agg(
                Jumlah_Pelanggan=("customer_unique_id", "count"),
                Avg_Recency=("Recency", "mean"),
                Avg_Frequency=("Frequency", "mean"),
                Avg_Monetary=("Monetary", "mean")
            )
            .reset_index()
            .round(2)
        )
        rfm_summary.columns = [
            "Segmen", "Jumlah Pelanggan",
            "Rata-rata Recency (Hari)", "Rata-rata Frequency", "Rata-rata Monetary (R$)"
        ]
        st.dataframe(rfm_summary, use_container_width=True, hide_index=True)
    else:
        st.info("Kolom `Customer_Segment` tidak ditemukan. Pastikan analisis RFM sudah dijalankan di notebook dan hasilnya tersimpan di main_data.csv.")
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TREN PESANAN
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Tren Penjualan")

    trend_df = filtered_df.copy()
    trend_df["year_month"] = trend_df["order_purchase_timestamp"].dt.to_period("M")
    trend_df["year"] = trend_df["order_purchase_timestamp"].dt.year

    monthly = (
        trend_df.groupby("year_month")
        .agg(total_orders=("order_id", "nunique"))
        .reset_index()
    )
    monthly["year_month_str"] = monthly["year_month"].astype(str)

    yearly = (
        trend_df.groupby("year")
        .agg(total_orders=("order_id", "nunique"))
        .reset_index()
    )

    # ── Tren Bulanan & Tahunan ────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Bulanan
    axes[0].plot(monthly["year_month_str"], monthly["total_orders"],
                 color="#3B82F6", linewidth=2, marker="o", markersize=4)
    axes[0].fill_between(monthly["year_month_str"], monthly["total_orders"],
                         alpha=0.12, color="#3B82F6")
    tick_step = max(1, len(monthly) // 10)
    axes[0].set_xticks(range(0, len(monthly), tick_step))
    axes[0].set_xticklabels(monthly["year_month_str"][::tick_step],
                             rotation=45, ha="right", fontsize=9)
    axes[0].set_title("Tren Penjualan Bulanan", fontsize=13)
    axes[0].set_xlabel("Bulan")
    axes[0].set_ylabel("Jumlah Penjualan")
    axes[0].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )

    # Tahunan
    bars = axes[1].bar(yearly["year"].astype(str), yearly["total_orders"],
                       color="#3B82F6", edgecolor="none", width=0.5)
    for bar, val in zip(bars, yearly["total_orders"]):
        axes[1].text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 100,
                     f"{val:,}", ha="center", fontsize=10)
    axes[1].set_title("Tren Penjualan Tahunan", fontsize=13)
    axes[1].set_xlabel("Tahun")
    axes[1].set_ylabel("Jumlah Penjualan")
    axes[1].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Distribusi per Hari ───────────────────────────────────────────────────
    st.markdown("**Distribusi Penjualan per Hari dalam Seminggu**")
    trend_df["day_of_week"] = trend_df["order_purchase_timestamp"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = trend_df["day_of_week"].value_counts().reindex(day_order).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4))
    colors_day = ["#3B82F6" if d not in ["Saturday", "Sunday"] else "#F59E0B"
                  for d in day_order]
    bars = ax.bar(day_counts.index, day_counts.values,
                  color=colors_day, edgecolor="none", width=0.6)
    for bar, val in zip(bars, day_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f"{int(val):,}", ha="center", fontsize=9)
    ax.set_ylabel("Jumlah Penjualan")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#3B82F6", label="Hari kerja"),
        Patch(facecolor="#F59E0B", label="Akhir pekan")
    ]
    ax.legend(handles=legend_elements, fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Pelanggan per Negara Bagian ───────────────────────────────────────────
    st.markdown("**Top 10 Negara Bagian dengan Pelanggan Terbanyak**")
    state_counts = (
        filtered_df.groupby("customer_state")["customer_unique_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    state_counts.columns = ["Negara Bagian", "Jumlah Pelanggan Unik"]

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(state_counts["Negara Bagian"], state_counts["Jumlah Pelanggan Unik"],
                  color=sns.color_palette("Blues_r", 10), edgecolor="none", width=0.6)
    for bar, val in zip(bars, state_counts["Jumlah Pelanggan Unik"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                f"{val:,}", ha="center", fontsize=9)
    ax.set_xlabel("Negara Bagian")
    ax.set_ylabel("Jumlah Pelanggan Unik")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9CA3AF;font-size:12px;'>"
    "Brazilian E-Commerce Public Dataset · Analisis Data · 2016–2018"
    "</p>",
    unsafe_allow_html=True
)
