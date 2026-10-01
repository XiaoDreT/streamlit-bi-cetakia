import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_quotation_data
from utils.intelligence_engine import rebuild_quotation_opportunity_metrics
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    render_section_info, render_summary_strip,
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Sales Intelligence Dashboard", page_icon="🎯", layout="wide")

# Load Datasets
df_quotes = load_quotation_data()

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_quotes.copy()
if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["sales_intel_title"],
    subtitle="Analisis Funnel Konversi Penawaran, Titik Drop-off, Status Peluang & Penyelamatan Omzet" if lang_code == "ID" else "Quotation Conversion Funnel, Drop-off Analysis, Opportunity Status & Revenue Recovery",
    module_tag="SALES MANAGEMENT / COMMERCIAL"
)

# -------------------------------------------------------------
# STRICT OPPORTUNITY CALCULATIONS (BUSINESS LOGIC ENGINE)
# -------------------------------------------------------------
opp = rebuild_quotation_opportunity_metrics(df_filtered)

# 4 Key Decision Support KPI Cards
q1, q2, q3, q4 = st.columns(4)
with q1:
    kpi1_title = "Total Nilai Penawaran (Pipeline)" if lang_code == "ID" else "Total Pipeline Value"
    kpi1_sub = f"{opp['total_count']:,} total penawaran diterbitkan" if lang_code == "ID" else f"{opp['total_count']:,} total quotations issued"
    metric_card(kpi1_title, format_rupiah(opp["total_pipeline"]), subtext=kpi1_sub)

with q2:
    kpi2_title = "Nilai Berhasil Menjadi Pesanan (Won)" if lang_code == "ID" else "Converted Revenue (Won)"
    kpi2_sub = f"{opp['converted_count']:,} penawaran sukses disetujui" if lang_code == "ID" else f"{opp['converted_count']:,} quotes converted to orders"
    metric_card(
        kpi2_title, 
        format_rupiah(opp["converted_val"]), 
        delta=f"{opp['win_rate']:.1f}% Tingkat Konversi", 
        delta_color="positive", 
        subtext=kpi2_sub
    )

with q3:
    kpi3_title = "Peluang Masih Terbuka (Aktif)" if lang_code == "ID" else "Open Active Opportunities"
    kpi3_sub = f"{opp['open_opp_count']:,} penawaran aktif dinegosiasikan" if lang_code == "ID" else f"{opp['open_opp_count']:,} quotes in negotiation"
    metric_card(
        kpi3_title, 
        format_rupiah(opp["open_opp_val"]), 
        delta=f"{opp['open_opp_pct']:.1f}% dari pipeline", 
        delta_color="positive" if opp["open_opp_val"] > 0 else "negative", 
        subtext=kpi3_sub
    )

with q4:
    kpi4_title = "Peluang Hilang / Drop" if lang_code == "ID" else "Lost / Dropped Pipeline"
    kpi4_sub = f"{opp['lost_opp_count']:,} penawaran kedaluwarsa / ditolak" if lang_code == "ID" else f"{opp['lost_opp_count']:,} expired or rejected quotes"
    metric_card(
        kpi4_title, 
        format_rupiah(opp["lost_opp_val"]), 
        delta=f"{opp['lost_opp_pct']:.1f}% dari pipeline", 
        delta_color="negative", 
        subtext=kpi4_sub
    )

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD (DECISION SUPPORT)
# -------------------------------------------------------------
if lang_code == "EN":
    ic_title = "Quotation Pipeline Recovery Strategy & Lost Opportunity Salvage"
    ic_metric = f"{format_rupiah(opp['lost_opp_val'])} Dropped Pipeline ({opp['lost_opp_pct']:.1f}% of Total Pipeline)"
    ic_context = f"Analyzed across {opp['total_count']:,} quotations worth {format_rupiah(opp['total_pipeline'])} for branch '{filters['branch']}' and segment '{filters['segment']}'."
    ic_insight = f"The primary conversion leak happens at the Expired quotation stage ({opp['lost_opp_pct']:.1f}% value). Currently, {opp['open_opp_count']:,} open quotes worth {format_rupiah(opp['open_opp_val'])} require prompt follow-up before reaching expiry."
    ic_impacted = f"Sales Representatives, Branch Sales Managers, and B2B Client Accounts."
    ic_action = "Sales Management: Review open opportunities daily. Require 24-hour client outreach for quotations nearing expiration (<= 72h) and launch reactivation outreach for the top expired accounts."
    ic_badge = "SALES DECISION SUPPORT"
    ic_target = f"{opp['urgent_count']:,} Urgent Quotes (<= 72h) worth {format_rupiah(opp['urgent_val'])}"
else:
    ic_title = "Strategi Penyelamatan Pipeline Penawaran & Pemulihan Peluang Hilang"
    ic_metric = f"{format_rupiah(opp['lost_opp_val'])} Peluang Hilang ({opp['lost_opp_pct']:.1f}% dari Total Pipeline)"
    ic_context = f"Dianalisis dari {opp['total_count']:,} penawaran senilai {format_rupiah(opp['total_pipeline'])} pada cabang '{filters['branch']}' dan segmen '{filters['segment']}'."
    ic_insight = f"Titik drop-off terbesar terjadi pada tahap penawaran kedaluwarsa (Expired) yang menyerap {opp['lost_opp_pct']:.1f}% nilai penawaran. Saat ini terdapat {opp['open_opp_count']:,} peluang terbuka senilai {format_rupiah(opp['open_opp_val'])} yang mendesak untuk di-follow up sebelum kedaluwarsa."
    ic_impacted = f"Tim Sales Representative, Manajer Penjualan Cabang, dan Klien B2B Instansi/Industri."
    ic_action = "Manajemen Sales: Tinjau peluang terbuka setiap pagi. Wajibkan follow-up dalam 24 jam untuk penawaran dengan sisa masa berlaku <= 72 jam, serta lakukan reaktivasi pada akun-akun expired bernilai besar."
    ic_badge = "KEPUTUSAN STRATEGIS PENJUALAN"
    ic_target = f"{opp['urgent_count']:,} Penawaran Mendesak (<= 72 Jam) senilai {format_rupiah(opp['urgent_val'])}"

render_business_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    who_impacted=ic_impacted,
    action=ic_action,
    badge=ic_badge,
    target_entity=ic_target
)

st.markdown("---")

# -------------------------------------------------------------
# TABBED SALES INTELLIGENCE INTERFACE (USER-FRIENDLY & CLEAN)
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "🔻 Conversion Funnel & Drop-off",
        "📊 Opportunity Status Breakdown",
        "🎯 Sales Rep Performance & Win Rate",
        "⏳ Urgent Worklist (Expiry <= 72h)"
    ]
else:
    tab_labels = [
        "🔻 Funnel Konversi & Drop-off Pipeline",
        "📊 Rincian Status Peluang Penawaran",
        "🎯 Kinerja Sales Rep & Win Rate",
        "⏳ Worklist Penawaran Mendesak (<= 72 Jam)"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

# -------------------------------------------------------------
# TAB 1: FUNNEL KONVERSI & DROP-OFF PIPELINE
# -------------------------------------------------------------
with tab1:
    if lang_code == "EN":
        render_section_info(
            title="Quotation Conversion Funnel & Major Drop-off Stage",
            subtitle="Visualizing quotation progression from issuance to won order and pinpointing leakage stages.",
            what_it_shows="Quotations issued, count successfully won, dropped (lost/expired), primary drop-off point, and overall win rate.",
            why_important="Pinpoints where commercial revenue is lost so sales teams can focus negotiation and follow-up efforts.",
            simple_insight=f"Overall conversion rate (Win Rate) is <b>{opp['win_rate']:.1f}%</b>. The primary leakage point is <b>Expired Quotations</b> accounting for <b>{opp['lost_opp_pct']:.1f}%</b> of total pipeline value."
        )
        strip_funnel = [
            {"label": "1. Total Pipeline", "value": f"{opp['total_count']:,} Quotes", "desc": format_rupiah(opp["total_pipeline"]), "color": "#1E3A8A"},
            {"label": "2. Won Orders", "value": f"{opp['converted_count']:,} Quotes", "desc": format_rupiah(opp["converted_val"]), "color": "#10B981"},
            {"label": "3. Dropped / Lost", "value": f"{opp['lost_opp_count']:,} Quotes", "desc": format_rupiah(opp["lost_opp_val"]), "color": "#EF4444"},
            {"label": "4. Biggest Drop Stage", "value": "Expired Stage", "desc": f"{opp['lost_opp_pct']:.1f}% pipeline dropped", "color": "#F59E0B"},
            {"label": "5. Conversion Rate", "value": f"{opp['win_rate']:.1f}%", "desc": "Quote-to-order ratio", "color": "#3B82F6"}
        ]
    else:
        render_section_info(
            title="Funnel Konversi Penawaran & Titik Drop-off Terbesar",
            subtitle="Memvisualisasikan alur perjalanan penawaran harga dari diterbitkan hingga menjadi pesanan.",
            what_it_shows="Jumlah penawaran diterbitkan, berapa yang berhasil menjadi pesanan (Won), berapa yang drop (hilang/kedaluwarsa), titik kebocoran terbesar, dan conversion rate keseluruhan.",
            why_important="Mengidentifikasi di tahap mana perusahaan paling banyak kehilangan calon pendapatan, sehingga tim sales bisa fokus memperbaiki tahap tersebut.",
            simple_insight=f"Tingkat konversi (Win Rate) saat ini adalah <b>{opp['win_rate']:.1f}%</b>. Titik drop-off terbesar berada pada <b>Penawaran Kedaluwarsa (Expired)</b> sebesar <b>{opp['lost_opp_pct']:.1f}%</b> dari total nilai penawaran."
        )
        strip_funnel = [
            {"label": "1. Total Penawaran", "value": f"{opp['total_count']:,} Quotes", "desc": format_rupiah(opp["total_pipeline"]), "color": "#1E3A8A"},
            {"label": "2. Menjadi Pesanan (Won)", "value": f"{opp['converted_count']:,} Quotes", "desc": format_rupiah(opp["converted_val"]), "color": "#10B981"},
            {"label": "3. Peluang Drop / Hilang", "value": f"{opp['lost_opp_count']:,} Quotes", "desc": format_rupiah(opp["lost_opp_val"]), "color": "#EF4444"},
            {"label": "4. Titik Drop Terbesar", "value": "Tahap Expired", "desc": f"{opp['lost_opp_pct']:.1f}% omzet penawaran drop", "color": "#F59E0B"},
            {"label": "5. Tingkat Konversi", "value": f"{opp['win_rate']:.1f}%", "desc": "Rasio quote menjadi invoice", "color": "#3B82F6"}
        ]
    render_summary_strip(strip_funnel)
    
    col_f1, col_f2 = st.columns([6, 4])
    with col_f1:
        st.markdown("**" + ("Visualisasi Alur Corong (Funnel) Penawaran" if lang_code == "ID" else "Quotation Conversion Funnel Flow") + "**")
        if lang_code == "EN":
            funnel_labels = [
                f"Issued ({opp['total_count']:,} quotes)",
                f"Won / Converted ({opp['converted_count']:,} quotes)",
                f"Open / Active ({opp['open_opp_count']:,} quotes)",
                f"Dropped / Lost ({opp['lost_opp_count']:,} quotes)"
            ]
        else:
            funnel_labels = [
                f"Diterbitkan ({opp['total_count']:,} quotes)",
                f"Menjadi Pesanan / Won ({opp['converted_count']:,} quotes)",
                f"Peluang Terbuka / Aktif ({opp['open_opp_count']:,} quotes)",
                f"Drop / Hilang ({opp['lost_opp_count']:,} quotes)"
            ]
        funnel_vals = [opp["total_pipeline"], opp["converted_val"], opp["open_opp_val"], opp["lost_opp_val"]]
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels,
            x=funnel_vals,
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#1E3A8A", "#10B981", "#3B82F6", "#EF4444"]}
        ))
        apply_plotly_theme(fig_funnel, height=360)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col_f2:
        if lang_code == "EN":
            st.markdown(f"""
            <div class="cetakia-card" style="padding: 16px 18px; margin-top: 10px;">
                <h4 style="color: #3B82F6; margin-top: 0;">💡 Commercial Meaning for Business Teams</h4>
                <div style="font-size: 13.5px; line-height: 1.6; opacity: 0.9;">
                    <p><b>• Win Rate of {opp['win_rate']:.1f}%:</b> Out of every 100 quotes prepared by sales reps, approximately {int(round(opp['win_rate']))} convert into confirmed production orders.</p>
                    <p><b>• Primary Leakage Point:</b> Most dropped quotes are not explicitly rejected by clients, but silently pass their expiration date without proactive follow-up.</p>
                    <p><b>• Quick Win:</b> Rescuing just 10% of quotations near expiration could immediately recover tens of millions of IDR in commercial revenue.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cetakia-card" style="padding: 16px 18px; margin-top: 10px;">
                <h4 style="color: #3B82F6; margin-top: 0;">💡 Makna Angka Corong Bagi Tim Bisnis</h4>
                <div style="font-size: 13.5px; line-height: 1.6; opacity: 0.9;">
                    <p><b>• Rasio Konversi {opp['win_rate']:.1f}%:</b> Dari setiap 100 penawaran yang dibuat oleh sales, sekitar {int(round(opp['win_rate']))} penawaran sukses closing menjadi pesanan resmi.</p>
                    <p><b>• Titik Kebocoran Utama:</b> Sebagian besar penawaran tidak ditolak klien secara eksplisit, melainkan dibiarkan melewati masa berlaku (Expired) tanpa tindak lanjut.</p>
                    <p><b>• Potensi Cepat:</b> Menyelamatkan hanya 10% dari penawaran yang hampir kedaluwarsa berpotensi menambah omzet hingga ratusan juta rupiah secara instan.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: RINCIAN STATUS PELUANG (USER-FRIENDLY & STATUS CARDS)
# -------------------------------------------------------------
with tab2:
    if lang_code == "EN":
        render_section_info(
            title="Quotation Opportunity Status Breakdown",
            subtitle="Classifying commercial quotation opportunities into 5 clear operational statuses.",
            what_it_shows="Distribution across 5 statuses: Active / Negotiation, Accepted / Processing, Won (Converted to Order), Rejected, and Expired.",
            why_important="Provides clear visibility into pipeline health: confirmed revenue vs revenue still needing proactive deal closing.",
            simple_insight="<b>Won</b> status represents confirmed cashflow, <b>Accepted & Active</b> must be closely monitored, and <b>Expired</b> represents reactivation targets."
        )
    else:
        render_section_info(
            title="Rincian Status Peluang Penawaran",
            subtitle="Pemisahan status peluang komersial ke dalam 5 status operasional yang mudah dipahami.",
            what_it_shows="Distribusi penawaran dalam 5 status: Aktif / Negosiasi, Berlanjut / Disetujui, Selesai (Menjadi Pesanan), Hilang / Ditolak, dan Kedaluwarsa.",
            why_important="Memberikan pandangan menyeluruh mengenai kesehatan pipeline penjualan: berapa omzet yang sudah pasti didapat vs berapa yang masih bisa diperjuangkan.",
            simple_insight="Status <b>Selesai (Won)</b> mencerminkan uang masuk, status <b>Berlanjut & Aktif</b> adalah peluang yang harus dikawal ketat, dan status <b>Kedaluwarsa</b> adalah peluang reaktivasi."
        )
    
    # Classify into 5 user-friendly statuses
    def classify_status_friendly(row, is_en=False):
        c_flag = row.get("converted_flag", 0)
        q_stat = str(row.get("quotation_status", "")).lower()
        if is_en:
            if c_flag == 1:
                return "Won / Converted Order"
            elif q_stat == "accepted":
                return "Accepted / In Process"
            elif q_stat in ["draft", "sent"]:
                return "Active / In Negotiation"
            elif q_stat == "rejected":
                return "Rejected / Did Not Proceed"
            elif q_stat == "expired":
                return "Expired"
            else:
                return "Other"
        else:
            if c_flag == 1:
                return "Selesai / Menjadi Pesanan (Won)"
            elif q_stat == "accepted":
                return "Berlanjut / Disetujui (Accepted)"
            elif q_stat in ["draft", "sent"]:
                return "Aktif / Dalam Negosiasi"
            elif q_stat == "rejected":
                return "Hilang / Tidak Lanjut (Rejected)"
            elif q_stat == "expired":
                return "Kedaluwarsa (Expired)"
            else:
                return "Lainnya"

    df_filtered_stat = df_filtered.copy()
    is_en = (lang_code == "EN")
    df_filtered_stat["status_friendly"] = df_filtered_stat.apply(lambda r: classify_status_friendly(r, is_en=is_en), axis=1)
    
    status_summary = df_filtered_stat.groupby("status_friendly").agg(
        total_val=("net_quotation_value", "sum"),
        quote_count=("quotation_code", "count")
    ).reset_index()
    tot_pipeline_all = status_summary["total_val"].sum()
    status_summary["val_pct"] = (status_summary["total_val"] / tot_pipeline_all * 100) if tot_pipeline_all > 0 else 0
    
    # 5 Status Cards Row
    stat_color_map = {
        "Selesai / Menjadi Pesanan (Won)": "#10B981",
        "Won / Converted Order": "#10B981",
        "Berlanjut / Disetujui (Accepted)": "#06B6D4",
        "Accepted / In Process": "#06B6D4",
        "Aktif / Dalam Negosiasi": "#3B82F6",
        "Active / In Negotiation": "#3B82F6",
        "Hilang / Tidak Lanjut (Rejected)": "#EF4444",
        "Rejected / Did Not Proceed": "#EF4444",
        "Kedaluwarsa (Expired)": "#F59E0B",
        "Expired": "#F59E0B"
    }
    
    stat_strip_cards = []
    unit_quote = "Quotes" if is_en else "Penawaran"
    for _, row in status_summary.iterrows():
        s_name = row["status_friendly"]
        s_val = format_rupiah(row["total_val"])
        s_cnt = f"{row['quote_count']:,} {unit_quote} ({row['val_pct']:.1f}%)"
        s_color = stat_color_map.get(s_name, "#3B82F6")
        stat_strip_cards.append({
            "label": s_name,
            "value": s_val,
            "desc": s_cnt,
            "color": s_color
        })
    render_summary_strip(stat_strip_cards)
    
    col_st1, col_st2 = st.columns([6, 4])
    with col_st1:
        st.markdown("**" + ("Komposisi Nilai Pipeline per Status Peluang" if not is_en else "Pipeline Value Breakdown by Opportunity Status") + "**")
        fig_stat_bar = px.bar(
            status_summary.sort_values(by="total_val", ascending=True),
            x="total_val",
            y="status_friendly",
            orientation="h",
            color="status_friendly",
            text=status_summary.sort_values(by="total_val", ascending=True)["val_pct"].apply(lambda p: f" {p:.1f}%"),
            color_discrete_map=stat_color_map,
            labels={
                "total_val": "Nilai Penawaran (IDR)" if not is_en else "Quotation Value (IDR)", 
                "status_friendly": "Status Peluang" if not is_en else "Opportunity Status"
            }
        )
        fig_stat_bar.update_traces(
            textposition="outside",
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.2
        )
        apply_plotly_theme(fig_stat_bar, height=360)
        st.plotly_chart(fig_stat_bar, use_container_width=True)
        
    with col_st2:
        st.markdown("**" + ("Proporsi Jumlah Lembar Penawaran" if not is_en else "Proportion of Quotation Counts") + "**")
        fig_stat_pie = px.pie(
            status_summary,
            names="status_friendly",
            values="quote_count",
            hole=0.45,
            color="status_friendly",
            color_discrete_map=stat_color_map
        )
        fig_stat_pie.update_traces(textposition='inside', textinfo='percent+label')
        apply_plotly_theme(fig_stat_pie, height=360)
        st.plotly_chart(fig_stat_pie, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: KINERJA SALES REPRESENTATIVE & WIN RATE
# -------------------------------------------------------------
with tab3:
    if lang_code == "EN":
        render_section_info(
            title="Sales Representative Performance & Closing Win Rate",
            subtitle="Ranking sales reps by managed pipeline value, win rate effectiveness, and unconverted pipeline.",
            what_it_shows="Sales name, total issued quotes, count of won orders, win rate (%), and pending pipeline value.",
            why_important="Evaluates top deal-closers and identifies reps requiring assistance or negotiation coaching.",
            simple_insight="Reps with high pending pipeline should be supported by branch sales coordinators for immediate closing outreach."
        )
    else:
        render_section_info(
            title="Kinerja Sales Representative & Tingkat Keberhasilan (Win Rate)",
            subtitle="Peringkat tenaga penjualan berdasarkan nilai peluang yang ditangani dan efektivitas konversi penawaran.",
            what_it_shows="Nama sales, total penawaran diterbitkan, jumlah penawaran yang berhasil closing, tingkat keberhasilan (Win Rate %), serta nilai peluang yang belum tertutup.",
            why_important="Mengevaluasi sales rep terbaik dalam closing deal dan mengidentifikasi staf yang membutuhkan bimbingan atau asistensi negosiasi.",
            simple_insight="Sales dengan nilai penawaran tertahan tinggi perlu dibantu oleh Koordinator Cabang untuk melakukan penutupan transaksi (closing support)."
        )
    
    if not df_filtered.empty and "sales_name" in df_filtered.columns:
        rep_perf = df_filtered.groupby("sales_name").agg(
            total_pipeline=("net_quotation_value", "sum"),
            total_quotes=("quotation_code", "count"),
            won_quotes=("converted_flag", "sum"),
            won_val=("net_quotation_value", lambda s: s[df_filtered.loc[s.index, "converted_flag"] == 1].sum()),
            lost_val=("net_quotation_value", lambda s: s[df_filtered.loc[s.index, "converted_flag"] == 0].sum())
        ).reset_index()
        
        rep_perf["win_rate"] = (rep_perf["won_quotes"] / rep_perf["total_quotes"] * 100).round(1)
        
        col_r1, col_r2 = st.columns([6, 4])
        with col_r1:
            st.markdown("**" + ("Peringkat Peluang Belum Terkonversi per Sales Rep" if lang_code == "ID" else "Pending / Lost Pipeline by Sales Rep") + "**")
            fig_rep = px.bar(
                rep_perf.sort_values(by="lost_val", ascending=False).head(10),
                x="lost_val",
                y="sales_name",
                orientation="h",
                color="lost_val",
                color_continuous_scale=["#FCA5A5", "#DC2626"],
                labels={
                    "lost_val": "Nilai Tertahan / Hilang (IDR)" if lang_code == "ID" else "Pending/Lost Pipeline (IDR)", 
                    "sales_name": "Sales Representative"
                }
            )
            fig_rep.update_traces(
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_rep, height=360)
            st.plotly_chart(fig_rep, use_container_width=True)
            
        with col_r2:
            st.markdown("**" + ("Tingkat Keberhasilan Closing (Win Rate %)" if lang_code == "ID" else "Closing Win Rate (%)") + "**")
            fig_win = px.bar(
                rep_perf.sort_values(by="win_rate", ascending=False).head(10),
                x="win_rate",
                y="sales_name",
                orientation="h",
                color="win_rate",
                text=rep_perf.sort_values(by="win_rate", ascending=False).head(10)["win_rate"].apply(lambda w: f"{w:.1f}%"),
                color_continuous_scale=["#93C5FD", "#10B981"],
                labels={"win_rate": "Win Rate (%)", "sales_name": "Sales Representative"}
            )
            fig_win.update_traces(textposition="outside")
            apply_plotly_theme(fig_win, height=360)
            st.plotly_chart(fig_win, use_container_width=True)
            
        st.markdown("**" + ("Tabel Rekapitulasi Lengkap Seluruh Sales Representative" if lang_code == "ID" else "Complete Performance Summary of All Sales Representatives") + "**")
        disp_rep = rep_perf.copy().sort_values(by="total_pipeline", ascending=False)
        disp_rep["Total Pipeline"] = disp_rep["total_pipeline"].apply(format_rupiah)
        disp_rep["Nilai Won (Closing)"] = disp_rep["won_val"].apply(format_rupiah)
        disp_rep["Nilai Belum Closing"] = disp_rep["lost_val"].apply(format_rupiah)
        disp_rep["Win Rate (%)"] = disp_rep["win_rate"].apply(lambda w: f"{w:.1f}%")
        quote_suffix = "lembar" if lang_code == "ID" else "quotes"
        disp_rep["Total Penawaran"] = disp_rep["total_quotes"].apply(lambda q: f"{q:,} {quote_suffix}")
        disp_rep["Closing Won"] = disp_rep["won_quotes"].apply(lambda w: f"{w:,} {quote_suffix}")
        
        if lang_code == "EN":
            rep_cols = {
                "sales_name": "Sales Representative",
                "Total Penawaran": "Issued Quotes",
                "Closing Won": "Won Orders",
                "Win Rate (%)": "Win Rate (%)",
                "Total Pipeline": "Total Pipeline",
                "Nilai Won (Closing)": "Won Revenue",
                "Nilai Belum Closing": "Pending / Lost Value"
            }
        else:
            rep_cols = {
                "sales_name": "Nama Sales Representative",
                "Total Penawaran": "Total Diterbitkan",
                "Closing Won": "Closing Sukses",
                "Win Rate (%)": "Tingkat Keberhasilan (Win Rate)",
                "Total Pipeline": "Total Pipeline",
                "Nilai Won (Closing)": "Nilai Won",
                "Nilai Belum Closing": "Nilai Tertahan / Hilang"
            }
        st.dataframe(
            disp_rep[["sales_name", "Total Penawaran", "Closing Won", "Win Rate (%)", "Total Pipeline", "Nilai Won (Closing)", "Nilai Belum Closing"]].rename(columns=rep_cols).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

# -------------------------------------------------------------
# TAB 4: WORKLIST PENAWARAN MENDESAK (TENGGAT <= 72 JAM)
# -------------------------------------------------------------
with tab4:
    if lang_code == "EN":
        render_section_info(
            title=f"Urgent Quotations Worklist - Expiring within <= 72 Hours ({opp['urgent_count']} Quotes)",
            subtitle="Active high-value quotations that will expire within the next 3 days unless followed up immediately.",
            what_it_shows="Quotation code, customer name, assigned sales rep, quotation value, remaining days to expiry, and current stage.",
            why_important="Prevents the largest pipeline leakage: quotations that lapse without client decision due to lack of follow-up.",
            simple_insight=f"There are <b>{opp['urgent_count']:,} active quotes</b> worth <b>{format_rupiah(opp['urgent_val'])}</b> that should be contacted via phone/WhatsApp today."
        )
    else:
        render_section_info(
            title=f"Daftar Kerja Penawaran Mendesak Tenggat <= 72 Jam ({opp['urgent_count']} Penawaran)",
            subtitle="Daftar penawaran aktif bernilai tinggi yang akan kedaluwarsa dalam 3 hari ke depan jika tidak segera ditindaklanjuti.",
            what_it_shows="Kode penawaran, nama pelanggan, sales rep penanggung jawab, nilai penawaran, sisa hari sebelum kedaluwarsa, dan status saat ini.",
            why_important="Mencegah kebocoran pipeline terbesar: penawaran yang sudah dibuat namun kedaluwarsa begitu saja tanpa kejelasan keputusan klien.",
            simple_insight=f"Terdapat <b>{opp['urgent_count']:,} penawaran aktif</b> senilai total <b>{format_rupiah(opp['urgent_val'])}</b> yang perlu ditelepon/di-WhatsApp hari ini juga."
        )
    
    urgent_quotes = df_filtered[
        (df_filtered["converted_flag"] == 0) & 
        (df_filtered["quotation_status"].isin(["draft", "sent", "accepted"])) & 
        (df_filtered["days_from_expiry"] <= 3)
    ].sort_values(by="net_quotation_value", ascending=False)
    
    if not urgent_quotes.empty:
        disp_urgent = urgent_quotes[["quotation_code", "customer_name", "sales_name", "net_quotation_value", "days_from_expiry", "quotation_status"]].copy()
        disp_urgent["Nilai Penawaran"] = disp_urgent["net_quotation_value"].apply(format_rupiah)
        if lang_code == "EN":
            disp_urgent["Sisa Waktu"] = disp_urgent["days_from_expiry"].apply(lambda d: f"{int(d)} Days Remaining" if pd.notnull(d) else "-")
            disp_urgent["Status Terakhir"] = disp_urgent["quotation_status"].map({
                "accepted": "Client Accepted (Processing Order)",
                "sent": "Sent to Client (Awaiting Decision)",
                "draft": "Sales Draft (Send Promptly)"
            }).fillna(disp_urgent["quotation_status"])
            urgent_rename = {
                "quotation_code": "Quotation Code",
                "customer_name": "Customer Name",
                "sales_name": "Sales Rep",
                "Nilai Penawaran": "Quotation Value",
                "Sisa Waktu": "Expiry Window",
                "Status Terakhir": "Current Status"
            }
        else:
            disp_urgent["Sisa Waktu"] = disp_urgent["days_from_expiry"].apply(lambda d: f"Sisa {int(d)} Hari" if pd.notnull(d) else "-")
            disp_urgent["Status Terakhir"] = disp_urgent["quotation_status"].map({
                "accepted": "Disetujui Klien (Proses Order)",
                "sent": "Terkirim ke Klien (Tunggu Keputusan)",
                "draft": "Draft Sales (Segera Kirimkan)"
            }).fillna(disp_urgent["quotation_status"])
            urgent_rename = {
                "quotation_code": "Kode Penawaran",
                "customer_name": "Nama Pelanggan",
                "sales_name": "Sales Rep",
                "Nilai Penawaran": "Nilai Penawaran",
                "Sisa Waktu": "Tenggat Waktu",
                "Status Terakhir": "Status Saat Ini"
            }
        
        st.dataframe(
            disp_urgent[["quotation_code", "customer_name", "sales_name", "Nilai Penawaran", "Sisa Waktu", "Status Terakhir"]].rename(columns=urgent_rename).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("✅ Tidak ada penawaran aktif terbuka yang berada dalam ambang batas kedaluwarsa 72 jam pada filter terpilih." if lang_code == "ID" else "✅ No open quotations are within 72 hours of expiration for current filters.")
