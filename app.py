import streamlit as st
import data_loader
import os
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Skin Guardian",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Auto-refresh the page every 15 minutes
st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")


# Load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()


# Data Fetching
@st.cache_data(
    ttl=60 * 5
)  # Cache for 5 minutes to ensure timely updates on autorefresh
def get_data():
    indoor = data_loader.get_latest_indoor_data()
    outdoor = data_loader.get_latest_outdoor_data()
    risks = data_loader.calculate_risk_factors(indoor, outdoor)
    indoor_history = data_loader.get_indoor_history_24h()
    outdoor_history = data_loader.get_outdoor_history_24h()
    return indoor, outdoor, risks, indoor_history, outdoor_history


indoor_data, outdoor_data, risk_factors, indoor_history, outdoor_history = get_data()

if not indoor_data or not outdoor_data:
    st.error(
        "Failed to load data from S3. Please ensure data exists and credentials are correct."
    )
    st.stop()


# UI Header
st.markdown(
    "<h1 class='hud-title'>SKIN_GUARDIAN<span class='blink'>_</span></h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='hud-subtitle'>// PREDICTIVE ENVIRONMENTAL DERMATOLOGICAL ANALYSIS</p>",
    unsafe_allow_html=True,
)

# --- Panel Selector ---
if "active_panel" not in st.session_state:
    st.session_state.active_panel = "Main Monitoring"

panels = ["Main Monitoring", "Historical Insights"]

# Style primary button as gradient pill, secondary as dim pill
st.markdown(
    """
    <style>
    /* Scope to the panel selector row only */
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) button {
        border-radius: 26px !important;
        padding: 8px 24px !important;
        font-family: monospace !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.09em !important;
        transition: all 0.22s ease !important;
    }
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) button[kind="secondary"] {
        border: 1px solid rgba(255,255,255,0.10) !important;
        background: rgba(255,255,255,0.04) !important;
        color: #64748b !important;
        font-weight: 600 !important;
    }
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) button[kind="secondary"]:hover {
        border-color: rgba(139,92,246,0.5) !important;
        color: #c4b5fd !important;
        background: rgba(139,92,246,0.12) !important;
        box-shadow: 0 0 14px rgba(139,92,246,0.20) !important;
    }
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) button[kind="primary"] {
        border: 1px solid rgba(139,92,246,0.6) !important;
        background: linear-gradient(130deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
        color: #fff !important;
        font-weight: 700 !important;
        box-shadow: 0 0 24px rgba(139,92,246,0.55), 0 2px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.18) !important;
    }
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) button[kind="primary"]:hover {
        box-shadow: 0 0 36px rgba(139,92,246,0.75), 0 2px 12px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.22) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

_panel_cols = st.columns(len(panels))
for _i, _p in enumerate(panels):
    _is_active = st.session_state.active_panel == _p
    _btn_type = "primary" if _is_active else "secondary"
    with _panel_cols[_i]:
        if st.button(_p, key=f"panel_btn_{_p}", use_container_width=True, type=_btn_type):
            st.session_state.active_panel = _p
            st.rerun()


# --- Section 1: Pre-Flight Check (Indoor Baseline) — Main Monitoring only ---
if st.session_state.active_panel == "Main Monitoring":
    st.markdown(
        "<h3 class='section-title'>INDOOR BASELINE</h3>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='section-subtitle'><span class='slash'>//</span> Your indoor environment dictates your baseline skin state before leaving.</p>",
        unsafe_allow_html=True,
    )

if st.session_state.active_panel == "Main Monitoring":
    st.markdown("<div style='margin-bottom: 20px;'>", unsafe_allow_html=True)
    # Determine orb color based on indoor humidity
    in_hum = indoor_data.get("humidity", 0)
    if in_hum > 60:
        core_color = "rgba(245, 158, 11, 0.8)"
        glow_color = "rgba(245, 158, 11, 0.25)"
        orb_badge = "<span class='badge badge-warning'>Oil Risk</span>"
    elif in_hum < 30:
        core_color = "rgba(239, 68, 68, 0.8)"
        glow_color = "rgba(239, 68, 68, 0.25)"
        orb_badge = "<span class='badge badge-danger'>Dehydration Alert</span>"
    else:
        core_color = "rgba(16, 185, 129, 0.8)"
        glow_color = "rgba(16, 185, 129, 0.25)"
        orb_badge = "<span class='badge badge-success'>Balanced</span>"

    in_temp = indoor_data.get("temperature", 22)
    if in_temp > 26:
        temp_badge = "<span class='badge badge-danger'>Too Hot</span>"
    elif in_temp < 18:
        temp_badge = "<span class='badge badge-purple'>Too Cold</span>"
    else:
        temp_badge = "<span class='badge badge-info'>Pleasant</span>"

    orb_html = f"""
<div class='orb-container' style='flex-direction: row; gap: 60px; flex-wrap: wrap; padding: 20px 0 40px 0;'>
<div style='display: flex; flex-direction: column; align-items: center;'>
<div class='status-orb' style='--core-color: rgba(59, 130, 246, 0.8); --glow-color: rgba(59, 130, 246, 0.25); box-shadow: 0 0 40px rgba(59, 130, 246, 0.25), inset 0 0 20px rgba(59, 130, 246, 0.2);'>
<div class='orb-ring'></div>
<div class='orb-text'>{indoor_data.get("temperature", "--")}°C</div>
<div class='orb-label'>INDOOR TEMP</div>
</div>
<div style='text-align: center; margin-top: 24px;'>
{temp_badge}
</div>
</div>
<div style='display: flex; flex-direction: column; align-items: center;'>
<div class='status-orb' style='--core-color: {core_color}; --glow-color: {glow_color}; box-shadow: 0 0 40px {glow_color}, inset 0 0 20px {glow_color};'>
<div class='orb-ring'></div>
<div class='orb-text'>{in_hum}%</div>
<div class='orb-label'>INDOOR HUMIDITY</div>
</div>
<div style='text-align: center; margin-top: 24px;'>
{orb_badge}
</div>
</div>
</div>
"""
    st.markdown(orb_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# HISTORICAL INSIGHTS PANEL
# =========================================================
if st.session_state.active_panel == "Historical Insights":
    st.markdown(
        "<h3 class='section-title'>24H TEMPERATURE &amp; HUMIDITY</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='section-subtitle'><span class='slash'>//</span> Indoor vs outdoor sensor readings with environmental shock bands.</p>",
        unsafe_allow_html=True,
    )

    TEMP_SHOCK_THRESHOLD = 5.0
    HUM_SHOCK_THRESHOLD = 15.0

    PLOT_BG = "rgba(10, 14, 26, 0)"
    GRID_COLOR = "rgba(255,255,255,0.07)"
    FONT_COLOR = "#94a3b8"
    TITLE_COLOR = "#e2e8f0"

    def _parse_time(t):
        return datetime.fromisoformat(t.replace("Z", "+00:00"))

    def _find_shock_bands(in_series, out_series, threshold):
        """Return list of (start, end) datetime tuples where |in-out| > threshold."""
        # Build a merged timeline
        in_map = {r["time"]: r for r in in_series}
        out_map = {r["time"]: r for r in out_series}
        all_times = sorted(set(list(in_map.keys()) + list(out_map.keys())))

        shock_times = []
        prev_in = prev_out = None
        for t in all_times:
            in_r = in_map.get(t)
            out_r = out_map.get(t)
            val_in = in_r["temperature"] if in_r else None
            val_out = out_r["temperature"] if out_r else None
            if val_in is None:
                val_in = prev_in
            if val_out is None:
                val_out = prev_out
            if val_in is not None and val_out is not None:
                if abs(val_out - val_in) > threshold:
                    shock_times.append(_parse_time(t))
            prev_in = val_in
            prev_out = val_out

        # Merge consecutive shock timestamps into bands
        bands = []
        if shock_times:
            start = shock_times[0]
            end = shock_times[0]
            for st_time in shock_times[1:]:
                if (st_time - end).total_seconds() < 7200:  # gap < 2h -> same band
                    end = st_time
                else:
                    bands.append((start, end))
                    start = end = st_time
            bands.append((start, end))
        return bands

    def _find_hum_shock_bands(in_series, out_series, threshold):
        in_map = {r["time"]: r for r in in_series}
        out_map = {r["time"]: r for r in out_series}
        all_times = sorted(set(list(in_map.keys()) + list(out_map.keys())))

        shock_times = []
        prev_in = prev_out = None
        for t in all_times:
            in_r = in_map.get(t)
            out_r = out_map.get(t)
            val_in = in_r["humidity"] if in_r else None
            val_out = out_r["humidity"] if out_r else None
            if val_in is None:
                val_in = prev_in
            if val_out is None:
                val_out = prev_out
            if val_in is not None and val_out is not None:
                if abs(val_out - val_in) > threshold:
                    shock_times.append(_parse_time(t))
            prev_in = val_in
            prev_out = val_out

        bands = []
        if shock_times:
            start = shock_times[0]
            end = shock_times[0]
            for st_time in shock_times[1:]:
                if (st_time - end).total_seconds() < 7200:
                    end = st_time
                else:
                    bands.append((start, end))
                    start = end = st_time
            bands.append((start, end))
        return bands

    def _make_chart(
        title,
        in_times,
        in_vals,
        out_times,
        out_vals,
        in_color,
        out_color,
        y_label,
        shock_bands,
    ):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=in_times,
                y=in_vals,
                mode="lines",
                name="Indoor",
                line=dict(color=in_color, width=2),
                hovertemplate="%{x|%H:%M}<br>Indoor: %{y:.1f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=out_times,
                y=out_vals,
                mode="lines",
                name="Outdoor",
                line=dict(color=out_color, width=2, dash="dot"),
                hovertemplate="%{x|%H:%M}<br>Outdoor: %{y:.1f}<extra></extra>",
            )
        )
        for band_start, band_end in shock_bands:
            fig.add_vrect(
                x0=band_start,
                x1=band_end,
                fillcolor="rgba(239,68,68,0.18)",
                layer="below",
                line_width=0,
                annotation_text="⚡ SHOCK",
                annotation_position="top left",
                annotation_font_size=10,
                annotation_font_color="#ef4444",
            )
        fig.update_layout(
            title=dict(text=title, font=dict(color=TITLE_COLOR, size=14), x=0),
            paper_bgcolor=PLOT_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, family="monospace"),
            xaxis=dict(
                gridcolor=GRID_COLOR,
                showgrid=True,
                tickformat="%H:%M",
                zeroline=False,
                title=None,
            ),
            yaxis=dict(
                gridcolor=GRID_COLOR,
                showgrid=True,
                zeroline=False,
                title=y_label,
                title_font=dict(color=FONT_COLOR),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=FONT_COLOR),
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=280,
            hovermode="x unified",
        )
        return fig

    # --- Temperature Chart ---
    in_temp_times = [
        _parse_time(r["time"])
        for r in indoor_history
        if r.get("temperature") is not None
    ]
    in_temp_vals = [
        r["temperature"] for r in indoor_history if r.get("temperature") is not None
    ]
    out_temp_times = [
        _parse_time(r["time"])
        for r in outdoor_history
        if r.get("temperature") is not None
    ]
    out_temp_vals = [
        r["temperature"] for r in outdoor_history if r.get("temperature") is not None
    ]
    temp_shock_bands = _find_shock_bands(
        indoor_history, outdoor_history, TEMP_SHOCK_THRESHOLD
    )

    # --- Humidity Chart ---
    in_hum_times = [
        _parse_time(r["time"]) for r in indoor_history if r.get("humidity") is not None
    ]
    in_hum_vals = [
        r["humidity"] for r in indoor_history if r.get("humidity") is not None
    ]
    out_hum_times = [
        _parse_time(r["time"]) for r in outdoor_history if r.get("humidity") is not None
    ]
    out_hum_vals = [
        r["humidity"] for r in outdoor_history if r.get("humidity") is not None
    ]
    hum_shock_bands = _find_hum_shock_bands(
        indoor_history, outdoor_history, HUM_SHOCK_THRESHOLD
    )

    if in_temp_times or out_temp_times:
        temp_fig = _make_chart(
            "🌡️ Temperature — Last 24H",
            in_temp_times,
            in_temp_vals,
            out_temp_times,
            out_temp_vals,
            in_color="#3b82f6",
            out_color="#f97316",
            y_label="°C",
            shock_bands=temp_shock_bands,
        )
        st.plotly_chart(temp_fig, use_container_width=True)
    else:
        st.info("No temperature history data available for the last 24 hours.")

    if in_hum_times or out_hum_times:
        hum_fig = _make_chart(
            "💧 Humidity — Last 24H",
            in_hum_times,
            in_hum_vals,
            out_hum_times,
            out_hum_vals,
            in_color="#06b6d4",
            out_color="#eab308",
            y_label="%",
            shock_bands=hum_shock_bands,
        )
        st.plotly_chart(hum_fig, use_container_width=True)
    else:
        st.info("No humidity history data available for the last 24 hours.")

    if temp_shock_bands or hum_shock_bands:
        st.markdown(
            "<p style='font-size:0.82rem; color:#ef4444; margin-top:4px;'>⚡ Red bands indicate Environmental Shock periods (ΔT > 5°C or ΔH > 15%).</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<h3 class='section-title' style='margin-top:40px;'>24H OUTDOOR THREATS</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='section-subtitle'><span class='slash'>//</span> Outdoor factors correlated to skin risk — shaded regions = active threat.</p>",
        unsafe_allow_html=True,
    )

    import plotly.subplots as psp

    # Skin-correlated outdoor threat definitions
    # (field, label, unit, risk_threshold, risk_direction, risk_color, risk_reason, line_color)
    THREAT_FACTORS = [
        {
            "field": "uvIndex",
            "label": "UV Index",
            "unit": "",
            "threshold": 5,
            "above": True,
            "risk_reason": "⚡ Oil surge",
            "line_color": "#f97316",
            "risk_color": "rgba(249,115,22,0.18)",
            "y_tickformat": ".0f",
        },
        {
            "field": "windSpeed",
            "label": "Wind Speed",
            "unit": "m/s",
            "threshold": 5.0,
            "above": True,
            "risk_reason": "💨 Moisture stripping",
            "line_color": "#38bdf8",
            "risk_color": "rgba(56,189,248,0.15)",
            "y_tickformat": ".1f",
        },
        {
            "field": "cloudCover",
            "label": "Cloud Cover",
            "unit": "%",
            "threshold": 70,
            "above": True,
            "risk_reason": "☁️ Dehydration driver",
            "line_color": "#a78bfa",
            "risk_color": "rgba(167,139,250,0.15)",
            "y_tickformat": ".0f",
        },
        {
            "field": "dewPoint",
            "label": "Dew Point",
            "unit": "°C",
            "threshold": 5,
            "above": False,  # Risk when BELOW threshold (very dry air)
            "risk_reason": "🌵 Barrier breakdown",
            "line_color": "#34d399",
            "risk_color": "rgba(52,211,153,0.15)",
            "y_tickformat": ".1f",
        },
    ]

    PLOT_BG2 = "rgba(10, 14, 26, 0)"
    GRID_COLOR2 = "rgba(255,255,255,0.07)"
    FONT_COLOR2 = "#94a3b8"
    TITLE_COLOR2 = "#e2e8f0"

    def _parse_dt(t):
        return datetime.fromisoformat(t.replace("Z", "+00:00"))

    def _risk_bands_1d(records, field, threshold, above):
        """Return (start, end) bands where field exceeds/is below threshold."""
        shock_ts = []
        for r in records:
            val = r.get(field)
            if val is None:
                continue
            in_risk = val >= threshold if above else val <= threshold
            if in_risk:
                shock_ts.append(_parse_dt(r["time"]))
        bands = []
        if shock_ts:
            s = e = shock_ts[0]
            for t in shock_ts[1:]:
                if (t - e).total_seconds() < 7200:
                    e = t
                else:
                    bands.append((s, e))
                    s = e = t
            bands.append((s, e))
        return bands

    if outdoor_history:
        n_rows = len(THREAT_FACTORS)
        fig_threats = psp.make_subplots(
            rows=n_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=[f["label"] for f in THREAT_FACTORS],
        )

        # Style subplot title fonts
        for ann in fig_threats.layout.annotations:
            ann.update(font=dict(color=TITLE_COLOR2, size=12))

        for i, fdef in enumerate(THREAT_FACTORS):
            row = i + 1
            times = [
                _parse_dt(r["time"])
                for r in outdoor_history
                if r.get(fdef["field"]) is not None
            ]
            vals = [
                r[fdef["field"]]
                for r in outdoor_history
                if r.get(fdef["field"]) is not None
            ]

            if not times:
                continue

            unit = fdef["unit"]
            fig_threats.add_trace(
                go.Scatter(
                    x=times,
                    y=vals,
                    mode="lines",
                    name=fdef["label"],
                    showlegend=False,
                    line=dict(color=fdef["line_color"], width=2),
                    hovertemplate=f"%{{x|%H:%M}}<br>{fdef['label']}: %{{y:.1f}}{unit}<extra></extra>",
                ),
                row=row,
                col=1,
            )

            # Add threshold reference line
            fig_threats.add_hline(
                y=fdef["threshold"],
                line=dict(color="rgba(239,68,68,0.4)", width=1, dash="dash"),
                row=row,
                col=1,
            )

            # Shade risk bands + annotate first band with reason
            bands = _risk_bands_1d(
                outdoor_history, fdef["field"], fdef["threshold"], fdef["above"]
            )
            for j, (bs, be) in enumerate(bands):
                fig_threats.add_vrect(
                    x0=bs,
                    x1=be,
                    fillcolor=fdef["risk_color"],
                    layer="below",
                    line_width=0,
                    row=row,
                    col=1,
                )
                if j == 0:
                    # Annotate only the first occurrence to avoid clutter
                    fig_threats.add_annotation(
                        x=bs,
                        y=fdef["threshold"],
                        xref=f"x{'' if row == 1 else row}",
                        yref=f"y{'' if row == 1 else row}",
                        text=fdef["risk_reason"],
                        showarrow=False,
                        xanchor="left",
                        yanchor="bottom",
                        font=dict(color="#ef4444", size=10),
                        bgcolor="rgba(0,0,0,0)",
                    )

            # Y-axis per row
            fig_threats.update_yaxes(
                tickformat=fdef["y_tickformat"],
                gridcolor=GRID_COLOR2,
                showgrid=True,
                zeroline=False,
                tickfont=dict(color=FONT_COLOR2, size=10),
                row=row,
                col=1,
            )

        # Shared x-axis (only bottom row shows labels)
        fig_threats.update_xaxes(
            gridcolor=GRID_COLOR2,
            tickformat="%H:%M",
            zeroline=False,
            tickfont=dict(color=FONT_COLOR2, size=10),
        )

        fig_threats.update_layout(
            paper_bgcolor=PLOT_BG2,
            plot_bgcolor=PLOT_BG2,
            font=dict(color=FONT_COLOR2, family="monospace"),
            margin=dict(l=0, r=0, t=40, b=0),
            height=160 * n_rows,
            hovermode="x unified",
            showlegend=False,
        )

        st.plotly_chart(fig_threats, use_container_width=True)
        st.markdown(
            "<p style='font-size:0.8rem; color:#64748b; margin-top:2px;'>"
            "Dashed red line = risk threshold. Shaded regions = active risk period. "
            "Factors: UV ≥ 5 → oil surge · Wind > 5 m/s → moisture loss · "
            "Cloud > 70% → dehydration · Dew Point ≤ 5°C → barrier breakdown</p>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No outdoor history data available for the last 24 hours.")


# When in Historical Insights mode, stop here — don't render Main Monitoring sections
if st.session_state.active_panel == "Historical Insights":
    st.stop()

# --- Section 3: Step Outside (Environmental Shock) ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 class='section-title'>ENVIRONMENTAL SHOCK</h3>", unsafe_allow_html=True
)
st.markdown(
    "<p class='section-subtitle'><span class='slash'>//</span> The sudden gap between indoor and outdoor triggers immediate skin reactions.</p>",
    unsafe_allow_html=True,
)

temp_diff = outdoor_data.get("temperature", 0) - indoor_data.get("temperature", 0)
hum_diff = outdoor_data.get("humidity", 0) - indoor_data.get("humidity", 0)

# Thermal Shock Thresholds
if -3 <= temp_diff <= 3:
    temp_shock_color = "#10b981"
    temp_label = "Safe"
elif temp_diff < -5 or temp_diff > 5:
    temp_shock_color = "#ef4444"
    temp_label = "Critical Threat"
else:
    temp_shock_color = "#f59e0b"
    temp_label = "Elevated Risk"

# Humidity Shock Thresholds
if -5 <= hum_diff <= 5:
    hum_shock_color = "#10b981"
    hum_label = "Safe"
elif hum_diff > 15 or hum_diff < -15:
    hum_shock_color = "#ef4444"
    hum_label = "Critical Dehydration"
else:
    hum_shock_color = "#f59e0b"
    hum_label = "Elevated Risk"

metrics_html_shock = f"""
<div class='metric-grid'>
    <div class='metric-box' style='--metric-color: {temp_shock_color};'>
        <div class='metric-val'>{temp_diff:+.1f}°C</div>
        <div class='metric-label'>Thermal Shock</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Gap between In/Out</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{temp_shock_color}; margin-top:12px;'>{temp_label}</div>
    </div>
    <div class='metric-box' style='--metric-color: {hum_shock_color};'>
        <div class='metric-val'>{hum_diff:+.1f}%</div>
        <div class='metric-label'>Humidity Shock</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Gap between In/Out</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{hum_shock_color}; margin-top:12px;'>{hum_label}</div>
    </div>
</div>
"""
st.markdown(metrics_html_shock, unsafe_allow_html=True)


# --- Section 3: Pure Outdoor Threats ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown("<h3 class='section-title'>OUTDOOR THREATS</h3>", unsafe_allow_html=True)
st.markdown(
    "<p class='section-subtitle'><span class='slash'>//</span> Direct outdoor factors that actively degrade your skin.</p>",
    unsafe_allow_html=True,
)

uv_val = outdoor_data.get("uvIndex", 0)
cloud_val = outdoor_data.get("cloudCover", 0)
wind_val = outdoor_data.get("windSpeed", 0)
dew_val = outdoor_data.get("dewPoint", 0)

# UV Index Thresholds
if uv_val <= 2:
    uv_color = "#10b981"
    uv_label = "Safe"
elif uv_val <= 5:
    uv_color = "#f59e0b"
    uv_label = "Elevated Risk"
else:
    uv_color = "#ef4444"
    uv_label = "Critical Oil Threat"

# Cloud Cover Thresholds
if cloud_val <= 30:
    cloud_color = "#10b981"
    cloud_label = "Safe"
elif cloud_val <= 70:
    cloud_color = "#f59e0b"
    cloud_label = "Elevated Risk"
else:
    cloud_color = "#ef4444"
    cloud_label = "Critical Dehydration"

# Wind Speed Thresholds (m/s)
if wind_val <= 2:
    wind_color = "#10b981"
    wind_label = "Calm"
elif wind_val <= 5:
    wind_color = "#f59e0b"
    wind_label = "Elevated Risk"
else:
    wind_color = "#ef4444"
    wind_label = "Moisture Stripping"

# Dew Point Thresholds (°C) — lower = drier air = more TEWL
if dew_val >= 10:
    dew_color = "#10b981"
    dew_label = "Comfortable"
elif dew_val >= 5:
    dew_color = "#f59e0b"
    dew_label = "Elevated Dryness"
else:
    dew_color = "#ef4444"
    dew_label = "Barrier Breakdown"

metrics_html_outdoor = f"""
<div class='metric-grid'>
    <div class='metric-box' style='--metric-color: {uv_color};'>
        <div class='metric-val'>{uv_val}</div>
        <div class='metric-label'>UV Index</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Primary oil driver</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{uv_color}; margin-top:12px;'>{uv_label}</div>
    </div>
    <div class='metric-box' style='--metric-color: {cloud_color};'>
        <div class='metric-val'>{cloud_val}%</div>
        <div class='metric-label'>Cloud Cover</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Water loss driver</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{cloud_color}; margin-top:12px;'>{cloud_label}</div>
    </div>
    <div class='metric-box' style='--metric-color: {wind_color};'>
        <div class='metric-val'>{wind_val:.1f} m/s</div>
        <div class='metric-label'>Wind Speed</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Moisture stripping</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{wind_color}; margin-top:12px;'>{wind_label}</div>
    </div>
    <div class='metric-box' style='--metric-color: {dew_color};'>
        <div class='metric-val'>{dew_val}°C</div>
        <div class='metric-label'>Dew Point</div>
        <div style='font-size: 0.9rem; color: #94a3b8; margin-top: 6px;'>Air moisture / TEWL</div>
        <div style='display:inline-block; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:600; color:#fff; background-color:{dew_color}; margin-top:12px;'>{dew_label}</div>
    </div>
</div>
"""
st.markdown(metrics_html_outdoor, unsafe_allow_html=True)


# --- Section 4: Action Feed (Going Out Predictor) ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 class='section-title'>RECOMMENDED ACTIONS</h3>", unsafe_allow_html=True
)

actions = []

if risk_factors.get("thermal_shock", 0) > 5:
    actions.append(f"""
    <div class='glass-card active-card' style='--card-color: #b94a4a;'>
        <div class='card-title'>⚠️ High Temperature Shock ({risk_factors["thermal_shock"]:.1f}°C jump)</div>
        <div class='card-desc'>Entering a radically hotter environment. Expect slight hydration loss and rapid oil generation. Consider a light, mattifying moisturizer before leaving.</div>
    </div>
    """)

if risk_factors.get("elasticity_boost"):
    actions.append("""
    <div class='glass-card active-card' style='--card-color: #795a96;'>
        <div class='card-title'>✨ Elasticity Boost Opportunity</div>
        <div class='card-desc'>Outdoor humidity is currently higher than indoors. Stepping out will give your skin an elasticity boost, though you may generate slightly more oil.</div>
    </div>
    """)

if risk_factors.get("spring_back_risk"):
    actions.append("""
    <div class='glass-card active-card' style='--card-color: #4d7aab;'>
        <div class='card-title'>💧 Rapid 'Spring-Back' Warning</div>
        <div class='card-desc'>Your indoor baseline hydration is high. Stepping outside will cause a rapid loss of moisture due to the spring-back effect. Apply a sealing occlusive layer now.</div>
    </div>
    """)

if risk_factors.get("cloud_risk"):
    actions.append("""
    <div class='glass-card active-card' style='--card-color: #6282a8;'>
        <div class='card-title'>☁️ Cloud Cover Dehydration</div>
        <div class='card-desc'>Unique data pattern detected: Heavy clouds outside are strongly correlated with dehydration during trips. Pack a hydrating mist.</div>
    </div>
    """)

if risk_factors.get("uv_oil_risk"):
    actions.append(f"""
    <div class='glass-card active-card' style='--card-color: #b38237;'>
        <div class='card-title'>☀️ Peak UV Alert (Index: {outdoor_data.get("uvIndex", "--")})</div>
        <div class='card-desc'>High UV exposure outside will rapidly drive up oil production. Apply high SPF and oil-control layer.</div>
    </div>
    """)

if not actions:
    actions.append("""
    <div class='glass-card active-card' style='--card-color: #49856a;'>
        <div class='card-title'>✅ Clear skies ahead</div>
        <div class='card-desc'>No significant environmental shocks detected. Your skin is safe to go out as-is.</div>
    </div>
    """)

for action in actions:
    st.markdown(action, unsafe_allow_html=True)


# --- Section 5: Forecast Panel ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 class='section-title'>2-HOUR & 9-HOUR FORECAST</h3>", unsafe_allow_html=True
)
st.markdown(
    "<p class='section-subtitle'><span class='slash'>//</span> How current outdoor conditions will slowly affect your indoor baseline.</p>",
    unsafe_allow_html=True,
)

forecasts = []

if risk_factors.get("wind_crash_forecast"):
    forecasts.append(f"""<div class='forecast-box' style='--fc-color: #4d7aab;'>
<div class='fc-time-badge'>T+2 HOURS</div>
<div class='fc-title'>💨 Humidity Crash</div>
<div class='fc-desc'>Strong winds detected outside ({outdoor_data.get("windSpeed", 0):.1f} m/s). Your indoor air will become drier within 2 hours. Humidifier recommended.</div>
</div>""")
else:
    forecasts.append(f"""<div class='forecast-box' style='--fc-color: #49856a;'>
<div class='fc-time-badge'>T+2 HOURS</div>
<div class='fc-title'>🌬️ Humidity Stable</div>
<div class='fc-desc'>Winds are calm ({outdoor_data.get("windSpeed", 0):.1f} m/s). Indoor humidity should remain stable in the short term.</div>
</div>""")

# Using DewPoint as proxy for thermal lag prediction as per the analysis
dp = outdoor_data.get("dewPoint", 0)
if dp < 5:
    forecasts.append(f"""<div class='forecast-box' style='--fc-color: #478c9e;'>
<div class='fc-time-badge'>T+9 HOURS</div>
<div class='fc-title'>🌡️ Thermal Drift (Cooling)</div>
<div class='fc-desc'>Outdoor dew point drops ({dp}°C). Expect a gradual cooling of your indoor environment over the next 9 hours. This will reduce baseline oil but may dry skin long-term.</div>
</div>""")
else:
    forecasts.append(f"""<div class='forecast-box' style='--fc-color: #b38237;'>
<div class='fc-time-badge'>T+9 HOURS</div>
<div class='fc-title'>🌡️ Thermal Drift (Warming)</div>
<div class='fc-desc'>Outdoor dew point is high ({dp}°C). The 9-hour thermal lag will push indoor temperatures up, preventing excess baseline oil growth but increasing dehydration risk.</div>
</div>""")

st.markdown(
    "<div class='forecast-grid'>" + "".join(forecasts) + "</div>",
    unsafe_allow_html=True,
)
