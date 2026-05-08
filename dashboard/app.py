import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="TradeScope — Market Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #080b12;
    color: #eef0f8;
}
.main .block-container {
    padding: 0 2rem 3rem 2rem;
    max-width: 1400px;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

[data-testid="stSidebar"] {
    background: #090c14;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem; }
[data-testid="stSidebar"] label {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #3e4d62 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #101520 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #eef0f8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}
[data-testid="stMetric"] { background: transparent !important; }
hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1rem 0;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── THEME COLORS ─────────────────────────────────────────────────────────────

COLORS = {
    "bg":     "#080b12",
    "panel":  "#0c1018",
    "card":   "#101520",
    "border": "rgba(255,255,255,0.06)",
    "text1":  "#eef0f8",
    "text2":  "#7888a2",
    "text3":  "#3e4d62",
    "green":  "#1fd68a",
    "red":    "#f04a4a",
    "blue":   "#4a8cf7",
    "amber":  "#f5a623",
    "purple": "#a163f7",
}

# ─── LOAD DATA ────────────────────────────────────────────────────────────────

DATA_PATH = Path("C:/trade/data/processed/market_prices_clean")

@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["sma_20"]   = df["close"].rolling(20).mean()
    df["sma_50"]   = df["close"].rolling(50).mean()
    df["returns"]  = df["close"].pct_change() * 100
    df["vol_ma"]   = df["volume"].rolling(10).mean()
    df["high_low"] = df["high"] - df["low"]

    df["bb_mid"]   = df["close"].rolling(20).mean()
    df["bb_std"]   = df["close"].rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]

    delta     = df["close"].diff()
    gain      = delta.clip(lower=0).rolling(14).mean()
    loss      = (-delta.clip(upper=0)).rolling(14).mean()
    rs        = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

try:
    df = load_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    err_msg = str(e)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
        <div style="font-size:22px;color:#4a8cf7;line-height:1;">◈</div>
        <div>
            <div style="font-size:15px;font-weight:600;color:#eef0f8;letter-spacing:-0.01em;">TradeScope</div>
            <div style="font-size:9px;font-weight:600;letter-spacing:0.14em;color:#3e4d62;
                        text-transform:uppercase;font-family:'DM Mono',monospace;margin-top:1px;">
                Market Intelligence
            </div>
        </div>
    </div>
    <div style="height:1px;background:rgba(255,255,255,0.06);margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)

    if data_loaded:
        st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:0.14em;color:#3e4d62;text-transform:uppercase;font-family:DM Mono,monospace;margin-bottom:8px;">DATE RANGE</div>', unsafe_allow_html=True)

        date_options = {
            "1 Month":  30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year":   365,
            "All Time": len(df)
        }

        selected_range = st.selectbox("Range", list(date_options.keys()), index=2, label_visibility="collapsed")
        n_days = date_options[selected_range]
        dff = df.tail(n_days).copy()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:0.14em;color:#3e4d62;text-transform:uppercase;font-family:DM Mono,monospace;margin-bottom:8px;">CHART OVERLAYS</div>', unsafe_allow_html=True)

        show_sma20  = st.checkbox("SMA 20",          value=True)
        show_sma50  = st.checkbox("SMA 50",           value=True)
        show_bb     = st.checkbox("Bollinger Bands",  value=False)
        show_volume = st.checkbox("Volume",           value=True)
        show_rsi    = st.checkbox("RSI (14)",         value=False)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:0.14em;color:#3e4d62;text-transform:uppercase;font-family:DM Mono,monospace;margin-bottom:8px;">CHART TYPE</div>', unsafe_allow_html=True)

        chart_type = st.selectbox("Type", ["Line", "Candlestick", "Area"], index=0, label_visibility="collapsed")

    st.markdown("""
    <div style="position:absolute;bottom:20px;left:0;right:0;padding:0 1.2rem;">
        <div style="height:1px;background:rgba(255,255,255,0.06);margin-bottom:12px;"></div>
        <div style="font-size:9px;font-weight:700;letter-spacing:0.12em;color:#4a8cf7;
                    font-family:'DM Mono',monospace;">SPARK · PARQUET</div>
        <div style="font-size:9px;color:#3e4d62;font-family:'DM Mono',monospace;margin-top:2px;">
            Apache Spark Pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

if not data_loaded:
    st.markdown(f"""
    <div style="background:#101520;border:1px solid rgba(240,74,74,0.2);border-radius:12px;
                padding:32px;text-align:center;margin-top:40px;">
        <div style="font-size:28px;margin-bottom:12px;">⚠</div>
        <div style="font-size:15px;font-weight:600;color:#eef0f8;margin-bottom:8px;">Data not found</div>
        <div style="font-size:12px;color:#7888a2;font-family:'DM Mono',monospace;">{err_msg}</div>
        <div style="font-size:11px;color:#3e4d62;margin-top:12px;">
            Expected path: C:/trade/data/processed/market_prices_clean
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── TOPBAR ───────────────────────────────────────────────────────────────────

latest    = dff.iloc[-1]
prev      = dff.iloc[-2]
change    = latest["close"] - prev["close"]
chg_pct   = (change / prev["close"]) * 100
is_up     = change >= 0
chg_color = COLORS["green"] if is_up else COLORS["red"]
chg_arrow = "▲" if is_up else "▼"

period_high = dff["high"].max()  if "high"   in dff.columns else dff["close"].max()
period_low  = dff["low"].min()   if "low"    in dff.columns else dff["close"].min()
period_ret  = ((dff["close"].iloc[-1] / dff["close"].iloc[0]) - 1) * 100
avg_vol     = dff["volume"].mean() if "volume" in dff.columns else 0
volatility  = dff["returns"].std()

st.markdown(f"""
<div style="background:{COLORS['panel']};border-bottom:1px solid {COLORS['border']};
            padding:18px 2rem;margin:0 -2rem 28px -2rem;
            display:flex;align-items:center;justify-content:space-between;">
    <div>
        <div style="font-size:18px;font-weight:500;color:{COLORS['text1']};letter-spacing:-0.01em;">
            Market Price Dashboard
        </div>
        <div style="font-size:11px;color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-top:3px;">
            {selected_range} · {len(dff):,} trading days · Last updated {latest['date'].strftime('%d %b %Y')}
        </div>
    </div>
    <div>
        <div style="background:{chg_color}22;border:1px solid {chg_color}44;border-radius:20px;
                    padding:5px 12px;font-size:11px;font-weight:700;color:{chg_color};
                    font-family:'DM Mono',monospace;letter-spacing:0.04em;">
            {chg_arrow} {abs(chg_pct):.2f}% TODAY
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────

def kpi_card(label, value, sub, accent_color, bar_pct=60):
    return f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:20px 22px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:{accent_color};border-radius:12px 12px 0 0;"></div>
        <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                    color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-bottom:10px;">
            {label}
        </div>
        <div style="font-size:28px;font-weight:300;letter-spacing:-0.02em;
                    color:{COLORS['text1']};margin-bottom:4px;">
            {value}
        </div>
        <div style="font-size:10px;color:{COLORS['text3']};font-family:'DM Mono',monospace;
                    margin-bottom:12px;">
            {sub}
        </div>
        <div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:{bar_pct}%;background:{accent_color};border-radius:2px;"></div>
        </div>
    </div>"""

close_bar = min(((latest["close"] - period_low) / (period_high - period_low)) * 100, 100) if period_high != period_low else 50
rsi_val   = f"{latest['rsi']:.1f}" if "rsi" in dff.columns and not pd.isna(latest["rsi"]) else "—"
rsi_bar   = float(latest["rsi"]) if "rsi" in dff.columns and not pd.isna(latest["rsi"]) else 50
rsi_color = (COLORS["red"]   if (not pd.isna(latest.get("rsi", float("nan"))) and latest.get("rsi", 50) > 70) else
             COLORS["green"] if (not pd.isna(latest.get("rsi", float("nan"))) and latest.get("rsi", 50) < 30) else
             COLORS["blue"])

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(kpi_card("Close Price", f"{latest['close']:,.2f}", f"High: {period_high:,.2f}", COLORS["blue"], close_bar), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Daily Change", f"{chg_arrow} {abs(change):,.2f}", f"{abs(chg_pct):.2f}% vs yesterday", chg_color, min(abs(chg_pct) * 5, 100)), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Period Return", f"{'+' if period_ret >= 0 else ''}{period_ret:.1f}%", f"{selected_range} performance", COLORS["green"] if period_ret >= 0 else COLORS["red"], min(abs(period_ret), 100)), unsafe_allow_html=True)
with c4:
    vol_str = f"{int(latest['volume']):,}" if "volume" in dff.columns else "—"
    st.markdown(kpi_card("Volume", vol_str, f"Avg: {int(avg_vol):,}", COLORS["amber"], 60), unsafe_allow_html=True)
with c5:
    st.markdown(kpi_card("RSI (14)", rsi_val, "Overbought >70 · Oversold <30", rsi_color, rsi_bar), unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ─── CHART BUILDER ────────────────────────────────────────────────────────────

rows = 1
row_h = [1]
subplot_titles = [""]

if show_volume:
    rows += 1
    row_h.append(0.25)
    subplot_titles.append("")

if show_rsi:
    rows += 1
    row_h.append(0.2)
    subplot_titles.append("")

fig = make_subplots(
    rows=rows, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=row_h,
    subplot_titles=subplot_titles
)

if chart_type == "Candlestick" and all(c in dff.columns for c in ["open", "high", "low", "close"]):
    fig.add_trace(go.Candlestick(
        x=dff["date"], open=dff["open"], high=dff["high"], low=dff["low"], close=dff["close"],
        name="OHLC",
        increasing_line_color=COLORS["green"], decreasing_line_color=COLORS["red"],
        increasing_fillcolor=COLORS["green"] + "55", decreasing_fillcolor=COLORS["red"] + "55",
        line_width=1
    ), row=1, col=1)
elif chart_type == "Area":
    fig.add_trace(go.Scatter(
        x=dff["date"], y=dff["close"], mode="lines", name="Close",
        line=dict(color=COLORS["blue"], width=2),
        fill="tozeroy", fillcolor=COLORS["blue"] + "18"
    ), row=1, col=1)
else:
    fig.add_trace(go.Scatter(
        x=dff["date"], y=dff["close"], mode="lines", name="Close",
        line=dict(color=COLORS["blue"], width=2)
    ), row=1, col=1)

if show_sma20:
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["sma_20"], mode="lines", name="SMA 20",
        line=dict(color=COLORS["amber"], width=1.2, dash="dot"), opacity=0.85), row=1, col=1)

if show_sma50:
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["sma_50"], mode="lines", name="SMA 50",
        line=dict(color=COLORS["purple"], width=1.2, dash="dash"), opacity=0.85), row=1, col=1)

if show_bb:
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["bb_upper"], mode="lines", name="BB Upper",
        line=dict(color=COLORS["green"], width=1, dash="dot"), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["bb_lower"], mode="lines", name="BB Lower",
        line=dict(color=COLORS["green"], width=1, dash="dot"),
        fill="tonexty", fillcolor=COLORS["green"] + "08", opacity=0.5), row=1, col=1)

vol_row = None
rsi_row = None

if show_volume and "volume" in dff.columns:
    vol_row = 2
    vol_colors = [COLORS["green"] if dff["close"].iloc[i] >= dff["close"].iloc[i - 1]
                  else COLORS["red"] for i in range(len(dff))]
    fig.add_trace(go.Bar(x=dff["date"], y=dff["volume"], name="Volume",
        marker_color=vol_colors, marker_opacity=0.6, showlegend=False), row=vol_row, col=1)
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["vol_ma"], mode="lines", name="Vol MA",
        line=dict(color=COLORS["amber"], width=1), showlegend=False), row=vol_row, col=1)

if show_rsi and "rsi" in dff.columns:
    rsi_row = (vol_row or 1) + 1
    fig.add_trace(go.Scatter(x=dff["date"], y=dff["rsi"], mode="lines", name="RSI",
        line=dict(color=COLORS["purple"], width=1.5), showlegend=False), row=rsi_row, col=1)
    for level, color in [(70, COLORS["red"]), (30, COLORS["green"])]:
        fig.add_hline(y=level, row=rsi_row, col=1,
            line_color=color, line_width=0.8, line_dash="dot", opacity=0.5)

fig.update_layout(
    height=560 + (80 if show_volume else 0) + (60 if show_rsi else 0),
    paper_bgcolor=COLORS["card"],
    plot_bgcolor=COLORS["card"],
    margin=dict(l=0, r=0, t=8, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)", font=dict(family="DM Mono", size=11, color=COLORS["text2"]), borderwidth=0),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1a2235", bordercolor="rgba(255,255,255,0.08)",
        font=dict(family="DM Mono", size=11, color=COLORS["text1"])),
    xaxis_rangeslider_visible=False,
    font=dict(family="DM Sans", color=COLORS["text2"]),
    dragmode="zoom"
)

axis_style = dict(
    gridcolor=COLORS["border"], linecolor=COLORS["border"],
    tickfont=dict(family="DM Mono", size=10, color=COLORS["text3"]),
    tickcolor=COLORS["border"], zeroline=False, showgrid=True,
)
fig.update_xaxes(**axis_style)
fig.update_yaxes(**axis_style)

st.markdown(f"""
<div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
            border-radius:12px;overflow:hidden;padding:20px 20px 8px 20px;margin-bottom:20px;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
        <div>
            <div style="font-size:13px;font-weight:600;color:{COLORS['text1']};">
                Price Chart — {chart_type}
            </div>
            <div style="font-size:10px;color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-top:2px;">
                {dff['date'].iloc[0].strftime('%d %b %Y')} → {dff['date'].iloc[-1].strftime('%d %b %Y')}
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(fig, use_container_width=True, config={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "filename": "tradescope_chart", "scale": 2}
})

st.markdown("</div>", unsafe_allow_html=True)

# ─── BOTTOM STATS ROW ─────────────────────────────────────────────────────────
# FIX: Use native st.columns() instead of a single HTML grid block.
# The original code embedded Python list comprehensions inside an f-string HTML block
# which caused Streamlit to render raw HTML source instead of the formatted UI.

def stat_row(k, v, value_color=None):
    color = value_color or COLORS['text1']
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;
                border-bottom:1px solid rgba(255,255,255,0.03);">
        <span style="font-size:11px;color:{COLORS['text2']};">{k}</span>
        <span style="font-size:11px;font-family:'DM Mono',monospace;color:{color};">{v}</span>
    </div>""", unsafe_allow_html=True)

def stat_card_header(title):
    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:12px 12px 0 0;padding:14px 20px 10px 20px;
                border-bottom:none;">
        <div style="font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:{COLORS['text3']};font-family:'DM Mono',monospace;">{title}</div>
    </div>
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:0 0 12px 12px;padding:4px 20px 16px 20px;border-top:none;">
    """, unsafe_allow_html=True)

def stat_card_footer():
    st.markdown("</div>", unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:18px 20px;">
        <div style="font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-bottom:14px;">
            PERIOD STATS
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Period High</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{period_high:,.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Period Low</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{period_low:,.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Price Range</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{period_high - period_low:,.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Volatility</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{volatility:.2f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Trading Days</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{len(dff):,}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    best_day  = dff['returns'].max()
    worst_day = dff['returns'].min()
    pos_days  = int((dff['returns'] > 0).sum())
    neg_days  = int((dff['returns'] < 0).sum())
    ret_color = COLORS["green"] if period_ret >= 0 else COLORS["red"]
    best_color  = COLORS["green"]
    worst_color = COLORS["red"]

    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:18px 20px;">
        <div style="font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-bottom:14px;">
            RETURNS BREAKDOWN
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Period Return</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{ret_color};">
                    {'+' if period_ret >= 0 else ''}{period_ret:.2f}%
                </span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Best Day</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{best_color};">+{best_day:.2f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Worst Day</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{worst_color};">{worst_day:.2f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Positive Days</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{pos_days:,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Negative Days</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{neg_days:,}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if "volume" in dff.columns:
        max_vol     = int(dff['volume'].max())
        min_vol     = int(dff['volume'].min())
        latest_vol  = int(latest['volume'])
        vs_avg      = f"{((latest['volume'] / avg_vol) - 1) * 100:+.1f}%" if avg_vol > 0 else "—"
    else:
        max_vol = min_vol = latest_vol = "—"
        vs_avg = "—"

    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:18px 20px;">
        <div style="font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                    color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-bottom:14px;">
            VOLUME ANALYSIS
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Avg Volume</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{int(avg_vol):,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Max Volume</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{max_vol:,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Min Volume</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{min_vol:,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">Latest Volume</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{latest_vol:,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:11px;color:{COLORS['text2']};">vs Avg</span>
                <span style="font-size:11px;font-family:'DM Mono',monospace;color:{COLORS['text1']};">{vs_avg}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ─── RETURNS DISTRIBUTION CHART ───────────────────────────────────────────────

ret_data = dff["returns"].dropna()

fig2 = go.Figure()
fig2.add_trace(go.Histogram(
    x=ret_data, nbinsx=60, name="Daily Returns",
    marker_color=COLORS["blue"], marker_opacity=0.7, marker_line_width=0
))
fig2.add_vline(x=0, line_color=COLORS["text3"], line_width=1, line_dash="dot")

fig2.update_layout(
    height=220,
    paper_bgcolor=COLORS["card"],
    plot_bgcolor=COLORS["card"],
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    bargap=0.05,
    hovermode="x",
    hoverlabel=dict(bgcolor="#1a2235", bordercolor="rgba(255,255,255,0.08)",
        font=dict(family="DM Mono", size=11, color=COLORS["text1"])),
    font=dict(family="DM Mono", color=COLORS["text2"]),
    xaxis=dict(title="Daily Return %", gridcolor=COLORS["border"], linecolor=COLORS["border"],
        tickfont=dict(family="DM Mono", size=10, color=COLORS["text3"]),
        zeroline=False, title_font=dict(size=10, color=COLORS["text3"])),
    yaxis=dict(title="Frequency", gridcolor=COLORS["border"], linecolor=COLORS["border"],
        tickfont=dict(family="DM Mono", size=10, color=COLORS["text3"]),
        zeroline=False, title_font=dict(size=10, color=COLORS["text3"]))
)

st.markdown(f"""
<div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
            border-radius:12px;padding:20px 20px 8px 20px;">
    <div style="font-size:13px;font-weight:600;color:{COLORS['text1']};margin-bottom:4px;">
        Returns Distribution
    </div>
    <div style="font-size:10px;color:{COLORS['text3']};font-family:'DM Mono',monospace;margin-bottom:16px;">
        Daily return frequency — {len(ret_data):,} observations
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)