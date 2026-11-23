"""Manufacturing OEE — public Streamlit dashboard (Streamlit Community Cloud)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOGO_PATH = ROOT / "screenshots" / "logo_white_square.png"

# Power BI Fluent / RAG (aligned with the original report)
PBI_BLUE = "#0078D4"
PBI_NAVY = "#1B365D"
PBI_CHART = "#118DFF"
PBI_NAVY_LINE = "#12239E"
PBI_ORANGE = "#E66C37"
PBI_GREEN = "#2E7D32"
PBI_AMBER = "#F2A900"
PBI_RED = "#C8102E"
PBI_DATA_COLORS = [
    "#118DFF",
    "#12239E",
    "#E66C37",
    "#6B007B",
    "#E044A7",
    "#744EC2",
    "#D9B300",
    "#D64550",
]


def inject_pbi_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
        html, body, [class*="css"] {{
            font-family: "Segoe UI", "Segoe UI Web", sans-serif;
        }}
        .stApp {{
            background-color: #F3F2F1;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PBI_NAVY} 0%, #142847 100%);
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stRadio label {{
            color: #FFFFFF !important;
        }}
        [data-testid="stSidebar"] .stRadio > div {{
            gap: 0.25rem;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(255, 255, 255, 0);
        }}
        .md-title {{
            font-size: 1.75rem;
            font-weight: 600;
            color: #242424;
            margin: 0 0 0.15rem 0;
        }}
        .md-subtitle {{
            font-size: 0.95rem;
            color: #616161;
            margin: 0 0 1rem 0;
        }}
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid #E6E6E6;
            border-radius: 8px;
            border-left: 4px solid {PBI_BLUE};
            padding: 14px 16px 12px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            min-height: 95px;
        }}
        .kpi-label {{
            font-size: 0.72rem;
            color: #616161;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 1.65rem;
            font-weight: 600;
            color: #242424;
            line-height: 1.2;
        }}
        .kpi-sub {{
            font-size: 0.78rem;
            color: #616161;
            margin-top: 6px;
        }}
        div[data-testid="stPlotlyChart"] {{
            background: #FFFFFF;
            border: 1px solid #E6E6E6;
            border-radius: 8px;
            padding: 0.35rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def rag_oee(oee: float) -> str:
    if oee >= 0.80:
        return PBI_GREEN
    if oee >= 0.70:
        return PBI_AMBER
    return PBI_RED


def rag_delivery(pct: float) -> str:
    if pct >= 0.95:
        return PBI_GREEN
    if pct >= 0.85:
        return PBI_AMBER
    return PBI_RED


def rag_production(vs_plan: float) -> str:
    if vs_plan >= 0.98:
        return PBI_GREEN
    if vs_plan >= 0.90:
        return PBI_AMBER
    return PBI_RED


def kpi_card(label: str, value: str, subtitle: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color: {accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(fig, height: int | None = None):
    title = fig.layout.title.text if fig.layout.title else ""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, sans-serif", size=11, color="#242424"),
        title=dict(
            text=title,
            font=dict(size=14, color="#242424"),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0,
            font=dict(size=10),
        ),
        margin=dict(l=12, r=12, t=44, b=56),
        height=height or 400,
        colorway=PBI_DATA_COLORS,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#F0F0F0",
        linecolor="#D1D1D1",
        tickfont=dict(color="#707070"),
        title_font=dict(color="#616161"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F0F0F0",
        linecolor="#D1D1D1",
        tickfont=dict(color="#707070"),
        title_font=dict(color="#616161"),
    )
    return fig


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    def one(val):
        if pd.isna(val):
            return pd.NaT
        if isinstance(val, str):
            val = val.strip()
            if val.isdigit():
                val = int(val)
        if isinstance(val, (int, float)) and val > 30_000:
            return pd.to_datetime(val, unit="D", origin="1899-12-30", errors="coerce")
        return pd.to_datetime(val, dayfirst=False, errors="coerce")

    return series.map(one)


@st.cache_data(ttl=3600)
def load_dims() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lines = pd.read_csv(DATA_DIR / "Dim_Line.csv")
    shifts = pd.read_csv(DATA_DIR / "Dim_Shift.csv")
    clients = pd.read_csv(DATA_DIR / "Dim_Client.csv")
    return lines, shifts, clients


@st.cache_data(ttl=3600)
def load_production() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Fact_Production.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    lines, _, _ = load_dims()
    df = df.merge(lines[["LineID", "LineName", "TargetOEE"]], on="LineID", how="left")
    return df


@st.cache_data(ttl=3600)
def load_downtime() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Fact_Downtime_RAW.csv")
    df["Date"] = parse_mixed_dates(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Category"] = (
        df["Category_Raw"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"un planned": "unplanned", "un-planned": "unplanned"})
    )
    df["Reason"] = df["DowntimeReason_Raw"].astype(str).str.strip().str.title()
    df["LineName"] = df["LineID_Raw"].astype(str).str.strip()
    return df


@st.cache_data(ttl=3600)
def load_defects() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Fact_Defects_RAW.csv")
    df["Date"] = parse_mixed_dates(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Reason"] = df["DefectReason_Raw"].astype(str).str.strip().str.title()
    return df


@st.cache_data(ttl=3600)
def load_orders() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Fact_Orders_RAW.csv")
    df["OrderDate"] = parse_mixed_dates(df["OrderDate"])
    df["PromisedDate"] = parse_mixed_dates(df["PromisedDate"])
    df["DispatchDate"] = parse_mixed_dates(df["DispatchDate"])
    df["Month"] = df["OrderDate"].dt.to_period("M").astype(str)
    df["Status"] = df["Status_Raw"].astype(str).str.strip().str.lower()
    on_time = df["DispatchDate"].notna() & df["PromisedDate"].notna()
    df.loc[on_time, "OnTime"] = df.loc[on_time, "DispatchDate"] <= df.loc[on_time, "PromisedDate"]
    return df


def oee_components(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"availability": 0.0, "performance": 0.0, "quality": 0.0, "oee": 0.0}
    run = df["RunTimeMins"].sum()
    plan_t = df["PlannedTimeMins"].sum()
    actual = df["ActualQty_KM"].sum()
    good = df["GoodQty_KM"].sum()
    plan_q = df["PlannedQty_KM"].sum()
    avail = run / plan_t if plan_t else 0.0
    perf_num = (actual / run) if run else 0.0
    perf_den = (plan_q / plan_t) if plan_t else 0.0
    perf = min(1.0, perf_num / perf_den) if perf_den else 0.0
    qual = good / actual if actual else 0.0
    oee = min(1.0, avail * perf * qual)
    return {
        "availability": avail,
        "performance": perf,
        "quality": qual,
        "oee": oee,
    }


def filter_production(
    df: pd.DataFrame,
    plants: list[str],
    lines: list[str],
    shifts: list[str],
    months: list[str],
) -> pd.DataFrame:
    out = df.copy()
    if plants:
        out = out[out["PlantID"].isin(plants)]
    if lines:
        out = out[out["LineID"].isin(lines)]
    if shifts:
        out = out[out["ShiftID"].isin(shifts)]
    if months:
        out = out[out["Month"].isin(months)]
    return out


def main() -> None:
    st.set_page_config(
        page_title="MD Executive Summary",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_pbi_css()

    production = load_production()
    dim_line, dim_shift, dim_client = load_dims()
    downtime = load_downtime()
    defects = load_defects()
    orders = load_orders()

    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=120)
        st.markdown("**Manufacturing Dashboard**")
        page = st.radio(
            "Páginas",
            [
                "Executive Overview",
                "Production & OEE",
                "Quality & Actions",
                "Sales & Orders",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Filtros globales")
        plants = st.multiselect(
            "Plant",
            sorted(production["PlantID"].dropna().unique()),
            default=None,
        )
        lines = st.multiselect(
            "Line",
            sorted(dim_line["LineID"].unique()),
            format_func=lambda x: dim_line.set_index("LineID").loc[x, "LineName"],
        )
        shifts = st.multiselect("Shift", sorted(dim_shift["ShiftID"].unique()))
        months = st.multiselect(
            "Month",
            sorted(production["Month"].dropna().unique()),
            default=None,
        )

    prod = filter_production(production, plants, lines, shifts, months)
    comp = oee_components(prod)

    if months:
        dt = downtime[downtime["Month"].isin(months)]
        def_f = defects[defects["Month"].isin(months)]
        ord_f = orders[orders["Month"].isin(months)]
    else:
        dt = downtime
        def_f = defects
        ord_f = orders

    prod_km = prod["GoodQty_KM"].sum()
    plan_km = prod["PlannedQty_KM"].sum()
    vs_plan = prod_km / plan_km if plan_km else 0
    closed = ord_f[ord_f["Status"].str.contains("close|dispatch", na=False)]
    on_time_pct = (
        closed["OnTime"].mean()
        if len(closed) and closed["OnTime"].notna().any()
        else float("nan")
    )
    backlog_cr = (
        ord_f[ord_f["Status"].isin(["open", "in progress", "inprogress"])]["OrderValue_INR"].sum()
        / 1e7
    )

    page_titles = {
        "Executive Overview": ("MD Executive Summary", "Weekly Exception Report"),
        "Production & OEE": ("Production & OEE", "Availability · Performance · Quality"),
        "Quality & Actions": ("Quality & Actions", "Scrap, defects & downtime"),
        "Sales & Orders": ("Sales & Orders", "Booking, backlog & segments"),
    }
    title, subtitle = page_titles[page]
    st.markdown(f'<p class="md-title">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="md-subtitle">{subtitle}</p>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        prod_label = f"{prod_km/1000:.2f}K km" if prod_km >= 1000 else f"{prod_km:,.0f} km"
        var = (vs_plan - 1) if plan_km else 0
        kpi_card(
            "Production (good km)",
            prod_label,
            f"vs Plan {plan_km/1000:,.2f}K ({var:+.1%})",
            rag_production(vs_plan),
        )
    with k2:
        oee_txt = f"{comp['oee']:.1%}"
        kpi_card("Overall OEE", oee_txt, "Target 80%", rag_oee(comp["oee"]))
    with k3:
        ot = f"{on_time_pct:.1%}" if not np.isnan(on_time_pct) else "—"
        kpi_card(
            "On-Time Delivery %",
            ot,
            "Target 95%",
            rag_delivery(on_time_pct) if not np.isnan(on_time_pct) else PBI_AMBER,
        )
    with k4:
        kpi_card(
            "Availability / Perf / Quality",
            f"{comp['availability']:.0%} · {comp['performance']:.0%} · {comp['quality']:.0%}",
            "OEE components",
            PBI_BLUE,
        )

    if page == "Executive Overview":
        by_line = pd.DataFrame(
            [
                {"LineName": line, "OEE": oee_components(g)["oee"]}
                for line, g in prod.groupby("LineName")
                if pd.notna(line)
            ]
        ).sort_values("OEE", ascending=True)
        fig = px.bar(
            by_line,
            x="OEE",
            y="LineName",
            orientation="h",
            title="OEE by line",
            color="OEE",
            color_continuous_scale=[[0, PBI_RED], [0.5, PBI_AMBER], [1, PBI_GREEN]],
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_layout(xaxis_tickformat=".0%")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            kpi_card("Order backlog (Cr)", f"{backlog_cr:,.2f}", "Open / in progress", PBI_BLUE)
        with c4:
            kpi_card(
                "Scrap rate (approx.)",
                f"{(1 - comp['quality']) if comp['quality'] else 0:.2%}",
                "Target below 2.5%",
                PBI_GREEN if comp["quality"] >= 0.975 else PBI_AMBER,
            )

    elif page == "Production & OEE":
        weekly = prod.dropna(subset=["Date"]).copy()
        weekly["Week"] = weekly["Date"].dt.to_period("W").astype(str)
        trend_rows = []
        for (line, week), g in weekly.groupby(["LineName", "Week"]):
            trend_rows.append(
                {"LineName": line, "Week": week, "OEE": oee_components(g)["oee"]}
            )
        trend = pd.DataFrame(trend_rows)
        if not trend.empty:
            fig2 = px.line(
                trend,
                x="Week",
                y="OEE",
                color="LineName",
                title="Weekly OEE trend",
                color_discrete_sequence=PBI_DATA_COLORS,
                markers=True,
            )
            fig2.update_layout(yaxis_tickformat=".0%")
            for trace in fig2.data:
                trace.line.width = 2.5
            st.plotly_chart(style_fig(fig2, 420), use_container_width=True)

        output = prod.groupby("LineName", as_index=False).agg(
            Actual_KM=("ActualQty_KM", "sum"),
            Planned_KM=("PlannedQty_KM", "sum"),
        )
        melted = output.melt(id_vars="LineName", var_name="Tipo", value_name="KM")
        fig3 = px.bar(
            melted,
            x="LineName",
            y="KM",
            color="Tipo",
            barmode="group",
            title="Output by line (km)",
            color_discrete_map={
                "Actual_KM": PBI_CHART,
                "Planned_KM": PBI_ORANGE,
            },
        )
        st.plotly_chart(style_fig(fig3, 400), use_container_width=True)

        comp_rows = pd.DataFrame(
            {
                "Component": ["Availability", "Performance", "Quality"],
                "Value": [comp["availability"], comp["performance"], comp["quality"]],
            }
        )
        fig_apq = px.bar(
            comp_rows,
            x="Component",
            y="Value",
            title="OEE breakdown",
            color="Component",
            color_discrete_map={
                "Availability": PBI_CHART,
                "Performance": PBI_NAVY_LINE,
                "Quality": PBI_GREEN,
            },
        )
        fig_apq.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(style_fig(fig_apq, 320), use_container_width=True)

    elif page == "Quality & Actions":
        scrap_pct = 1 - comp["quality"] if comp["quality"] else 0
        kpi_card(
            "Scrap % (1 − quality)",
            f"{scrap_pct:.2%}",
            "Target: below 2.5%",
            PBI_GREEN if scrap_pct <= 0.025 else PBI_AMBER if scrap_pct <= 0.04 else PBI_RED,
        )
        top_dt = (
            dt.groupby("Reason", as_index=False)["DowntimeMinutes"]
            .sum()
            .sort_values("DowntimeMinutes", ascending=False)
            .head(5)
        )
        if not top_dt.empty:
            fig4 = px.bar(
                top_dt,
                x="DowntimeMinutes",
                y="Reason",
                orientation="h",
                title="Top 5 downtime reasons",
                color_discrete_sequence=[PBI_NAVY_LINE],
            )
            st.plotly_chart(style_fig(fig4, 360), use_container_width=True)
        top_def = (
            def_f.groupby("Reason", as_index=False)["ScrapQty_KM"]
            .sum()
            .sort_values("ScrapQty_KM", ascending=False)
            .head(8)
        )
        if not top_def.empty:
            fig5 = px.bar(
                top_def,
                x="Reason",
                y="ScrapQty_KM",
                title="Scrap by defect reason (km)",
                color="ScrapQty_KM",
                color_continuous_scale=[[0, "#DEEFFF"], [1, PBI_CHART]],
            )
            fig5.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig5, 380), use_container_width=True)

    elif page == "Sales & Orders":
        ord_f = ord_f.copy()
        ord_f["ClientNorm"] = ord_f["Client_Raw"].astype(str).str.strip().str.lower()
        dc = dim_client.copy()
        dc["ClientNorm"] = dc["ClientName"].str.strip().str.lower()
        ord_f = ord_f.merge(dc[["ClientNorm", "Segment"]], on="ClientNorm", how="left")
        ord_f["Segment"] = ord_f["Segment"].fillna("Sin segmento")
        by_seg = (
            ord_f.groupby("Segment", as_index=False)["OrderValue_INR"]
            .sum()
            .sort_values("OrderValue_INR", ascending=False)
        )
        by_seg["OrderValue_Cr"] = by_seg["OrderValue_INR"] / 1e7
        if not by_seg.empty:
            fig6 = px.bar(
                by_seg,
                x="Segment",
                y="OrderValue_Cr",
                title="Order value by client segment (Cr INR)",
                color_discrete_sequence=[PBI_CHART],
            )
            st.plotly_chart(style_fig(fig6, 380), use_container_width=True)

        mtd = ord_f[ord_f["OrderDate"].notna()]
        if not mtd.empty:
            mtd = mtd.assign(Month=mtd["OrderDate"].dt.to_period("M").astype(str))
            monthly = (
                mtd.groupby("Month", as_index=False)["OrderValue_INR"]
                .sum()
                .assign(Cr=lambda d: d["OrderValue_INR"] / 1e7)
            )
            fig7 = px.line(
                monthly,
                x="Month",
                y="Cr",
                title="Order booking by month (Cr INR)",
                color_discrete_sequence=[PBI_NAVY_LINE],
                markers=True,
            )
            fig7.update_traces(line_width=2.5)
            st.plotly_chart(style_fig(fig7, 380), use_container_width=True)


if __name__ == "__main__":
    main()