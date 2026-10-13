"""
Streamlit Visualization Dashboard
Interactive dashboard for financial sentiment analysis results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from data_collector import NewsCollector, DATE_RANGE_PRESETS
from sentiment_analyzer import SentimentAnalyzer
from signal_generator import SignalGenerator
from query_generator import SmartQueryGenerator


# ── Page Configuration ────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Sentiment Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body,
    .stApp, .stMarkdown, .stText, .stCaption,
    .stTextInput, .stSelectbox, .stRadio, .stSlider,
    .stButton, .stMetric, .stDataFrame, .stTable,
    h1, h2, h3, h4, h5, h6, p, span, div, label, input, textarea, select,
    [data-testid="stSidebar"], [data-testid="stHeader"],
    [data-testid="stMainBlockContainer"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Preserve Streamlit icon fonts */
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    [class*="icon"],
    [data-testid="collapsedControl"] span {
        font-family: 'Material Symbols Rounded' !important;
    }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #a5b4fc;
        font-size: 1.05rem;
        margin: 0.5rem 0 0 0;
    }

    .signal-card {
        padding: 1.5rem 2rem;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: 2px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .signal-buy {
        background: linear-gradient(135deg, #064e3b, #059669);
        color: #d1fae5;
        border: 1px solid #34d399;
    }
    .signal-sell {
        background: linear-gradient(135deg, #7f1d1d, #dc2626);
        color: #fecaca;
        border: 1px solid #f87171;
    }
    .signal-hold {
        background: linear-gradient(135deg, #78350f, #d97706);
        color: #fef3c7;
        border: 1px solid #fbbf24;
    }

    .metric-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #4338ca;
    }
    .metric-card h3 {
        color: #a5b4fc;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 0.5rem 0;
    }
    .metric-card .value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .article-row {
        background: #1e1b4b;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #6366f1;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #1a1744);
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Cached Data Pipeline ─────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_analyzer():
    """Cache the FinBERT model so it loads only once."""
    return SentimentAnalyzer()


@st.cache_data(show_spinner=False, ttl=300)
def run_pipeline(_analyzer, query: str, days_back: int = 7, smart_query: bool = True):
    """Run the full analysis pipeline and cache results for 5 min."""
    collector = NewsCollector()
    articles, query_info = collector.fetch_articles(
        query=query, days_back=days_back, smart_query=smart_query
    )
    analyzed = _analyzer.analyze_articles(articles)

    generator = SignalGenerator()
    result = generator.aggregate_sentiment(analyzed)

    return analyzed, result, query_info


# ── Sidebar ──────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    query = st.text_input(
        "Search Query",
        value="stock market",
        help="E.g. 'tesla stocks', 'oil prices', 'banking sector', 'nvidia and amd'",
    )

    # ── Smart Query Toggle ────────────────────────────────────────
    st.markdown("### 🧠 Smart Query")
    smart_query_on = st.toggle("Expand query automatically", value=True,
        help="Detects companies, tickers, and sectors to build a richer search query")

    if smart_query_on and query:
        _preview = SmartQueryGenerator().generate(query)
        with st.expander("🔍 Query Preview", expanded=True):
            st.caption(f"**Original:** {_preview['original']}")
            st.caption(f"**Optimized:** {_preview['optimized']}")
            if _preview['entities']:
                ents = ", ".join(f"{e['name']} ({e['ticker']})" for e in _preview['entities'])
                st.caption(f"**Detected:** {ents}")
            st.caption(f"**Strategy:** {_preview['strategy']}")

    # ── Date Range Filter ─────────────────────────────────────────
    st.markdown("### 📅 Date Range")
    date_mode = st.radio("Time period", ["Preset", "Custom"], horizontal=True)

    if date_mode == "Preset":
        preset = st.selectbox("Select range", list(DATE_RANGE_PRESETS.keys()), index=1)
        days_back = DATE_RANGE_PRESETS[preset]
    else:
        days_back = st.slider("Days back", min_value=1, max_value=365, value=14)

    st.caption(f"Searching articles from the past **{days_back}** day(s)")

    st.markdown("---")
    st.markdown("### 📋 Model Info")
    st.markdown("""
    - **Model**: FinBERT (ProsusAI/finbert)
    - **Domain**: Financial text
    - **Labels**: Positive / Negative / Neutral
    """)

    st.markdown("---")
    run_btn = st.button("🚀 Run Analysis", use_container_width=True, type="primary")


# ── Header ───────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📈 Financial Sentiment Analyzer</h1>
    <p>Real-time sentiment analysis of financial news powered by FinBERT</p>
</div>
""", unsafe_allow_html=True)


# ── Main Pipeline ────────────────────────────────────────────────────

if run_btn or "analyzed" not in st.session_state:
    with st.spinner("🔄 Loading model and analyzing articles..."):
        analyzer = load_analyzer()
        analyzed, result, query_info = run_pipeline(
            analyzer, query, days_back=days_back, smart_query=smart_query_on
        )
        st.session_state["analyzed"] = analyzed
        st.session_state["result"] = result
        st.session_state["query_info"] = query_info

analyzed = st.session_state.get("analyzed", [])
result = st.session_state.get("result", {})

if not analyzed:
    st.warning("No articles to analyze. Please check your configuration.")
    st.stop()


# ── Row 1: Signal + Metrics ──────────────────────────────────────────

col_signal, col_m1, col_m2, col_m3 = st.columns([2, 1, 1, 1])

signal = result.get("signal", "HOLD")
score = result.get("aggregate_score", 0.0)

with col_signal:
    css_class = {"BUY": "signal-buy", "SELL": "signal-sell", "HOLD": "signal-hold"}.get(signal, "signal-hold")
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")
    st.markdown(f'<div class="signal-card {css_class}">{emoji} {signal}</div>', unsafe_allow_html=True)
    st.caption(f"Aggregate Sentiment Score: **{score:+.4f}**")

dist = result.get("distribution", {})
with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Articles</h3>
        <div class="value">{result.get('article_count', 0)}</div>
    </div>""", unsafe_allow_html=True)

with col_m2:
    pos = dist.get("positive", 0)
    st.markdown(f"""
    <div class="metric-card">
        <h3>Positive</h3>
        <div class="value" style="color: #34d399;">{pos}</div>
    </div>""", unsafe_allow_html=True)

with col_m3:
    neg = dist.get("negative", 0)
    st.markdown(f"""
    <div class="metric-card">
        <h3>Negative</h3>
        <div class="value" style="color: #f87171;">{neg}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ─────────────────────────────────────────────────────────────

tab_charts, tab_articles, tab_metrics = st.tabs(["📊 Charts", "📰 Articles", "⚡ Performance"])


# ── Tab 1: Charts ────────────────────────────────────────────────────

with tab_charts:
    chart_col1, chart_col2 = st.columns(2)

    # Pie Chart: Sentiment Distribution
    with chart_col1:
        st.subheader("Sentiment Distribution")
        pie_df = pd.DataFrame([
            {"Sentiment": "Positive", "Count": dist.get("positive", 0)},
            {"Sentiment": "Negative", "Count": dist.get("negative", 0)},
            {"Sentiment": "Neutral", "Count": dist.get("neutral", 0)},
        ])
        fig_pie = px.pie(
            pie_df, values="Count", names="Sentiment",
            color="Sentiment",
            color_discrete_map={"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#fbbf24"},
            hole=0.45,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            legend=dict(orientation="h", y=-0.15),
            margin=dict(t=20, b=40, l=20, r=20),
        )
        fig_pie.update_traces(textinfo="percent+label", textfont_size=13)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar Chart: Sentiment Scores per Article
    with chart_col2:
        st.subheader("Sentiment Scores by Article")
        bar_df = pd.DataFrame([
            {
                "Article": a.get("title", "")[:45] + "…" if len(a.get("title", "")) > 45 else a.get("title", ""),
                "Score": a.get("score", 0),
                "Label": a.get("label", "neutral").capitalize(),
            }
            for a in analyzed
        ])
        color_map = {"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#fbbf24"}
        fig_bar = px.bar(
            bar_df, x="Score", y="Article", orientation="h",
            color="Label", color_discrete_map=color_map,
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=11),
            yaxis=dict(autorange="reversed"),
            xaxis=dict(title="Sentiment Score", gridcolor="rgba(255,255,255,0.08)"),
            legend=dict(orientation="h", y=1.08),
            margin=dict(t=40, b=40, l=10, r=20),
            height=max(400, len(analyzed) * 36),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Sentiment Over Time
    st.subheader("Sentiment Over Time")
    time_data = []
    for a in analyzed:
        pub = a.get("publishedAt", "")
        if pub:
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                time_data.append({"Time": dt, "Score": a.get("score", 0), "Label": a.get("label", "neutral").capitalize()})
            except ValueError:
                pass

    if time_data:
        time_df = pd.DataFrame(time_data).sort_values("Time")
        color_map_time = {"Positive": "#34d399", "Negative": "#f87171", "Neutral": "#fbbf24"}
        fig_time = px.scatter(
            time_df, x="Time", y="Score", color="Label",
            color_discrete_map=color_map_time, size=[12] * len(time_df),
        )
        fig_time.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig_time.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            xaxis=dict(title="Published Date", gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(title="Sentiment Score", gridcolor="rgba(255,255,255,0.08)"),
            legend=dict(orientation="h", y=1.08),
            margin=dict(t=40, b=40),
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No timestamp data available for timeline view.")


# ── Tab 2: Articles Table ────────────────────────────────────────────

with tab_articles:
    st.subheader("Article-Level Sentiment Analysis")

    for article in analyzed:
        label = article.get("label", "neutral")
        conf = article.get("confidence", 0)
        score_val = article.get("score", 0)

        label_color = {"positive": "#34d399", "negative": "#f87171", "neutral": "#fbbf24"}.get(label, "#94a3b8")
        label_emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(label, "⚪")

        st.markdown(f"""
        <div style="background: #1e1b4b; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 0.7rem;
                    border-left: 4px solid {label_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="color: #e2e8f0; font-weight: 600; font-size: 0.95rem;">
                        {article.get('title', 'Untitled')}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 0.3rem;">
                        {article.get('source', '')} &nbsp;•&nbsp; {article.get('publishedAt', '')[:10]}
                    </div>
                </div>
                <div style="text-align: right; min-width: 140px;">
                    <span style="color: {label_color}; font-weight: 700; font-size: 0.95rem;">
                        {label_emoji} {label.upper()}
                    </span>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.2rem;">
                        Score: {score_val:+.4f} &nbsp;|&nbsp; Conf: {conf:.1%}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 3: Performance Metrics ────────────────────────────────────────

with tab_metrics:
    st.subheader("Performance Metrics")

    metrics = result.get("metrics", {})

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Articles Processed", result.get("article_count", 0))
    with m2:
        st.metric("Aggregation Latency", f"{metrics.get('latency_ms', 0):.2f} ms")
    with m3:
        st.metric("Buy Threshold", f"{metrics.get('buy_threshold', 0):+.2f}")
    with m4:
        st.metric("Sell Threshold", f"{metrics.get('sell_threshold', 0):+.2f}")

    st.markdown("---")

    st.subheader("Confidence Distribution")
    conf_values = [a.get("confidence", 0) for a in analyzed]
    if conf_values:
        fig_hist = px.histogram(
            x=conf_values, nbins=20,
            labels={"x": "Confidence Score", "y": "Count"},
            color_discrete_sequence=["#6366f1"],
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Score Detail Breakdown")
    detail_data = []
    for a in analyzed:
        sd = a.get("scores_detail", {})
        detail_data.append({
            "Article": a.get("title", "")[:50],
            "Positive": sd.get("positive", 0),
            "Negative": sd.get("negative", 0),
            "Neutral": sd.get("neutral", 0),
        })
    if detail_data:
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True, hide_index=True)


# ── Footer ───────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #64748b; font-size: 0.85rem;">'
    'Financial Sentiment Analysis System • Powered by FinBERT • Built with Streamlit'
    '</p>',
    unsafe_allow_html=True,
)
