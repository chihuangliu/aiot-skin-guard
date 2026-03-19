import streamlit as st
import data_loader
import os
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
    return indoor, outdoor, risks


indoor_data, outdoor_data, risk_factors = get_data()

if not indoor_data or not outdoor_data:
    st.error(
        "Failed to load data from S3. Please ensure data exists and credentials are correct."
    )
    st.stop()


# UI Header
st.markdown(
    "<h1 style='text-align: center; color: #fff; margin-bottom: 0;'>🛡️ Skin Guardian</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #a1a1aa; margin-top: 5px; margin-bottom: 40px;'>Predictive Environmental Dermatological Analysis</p>",
    unsafe_allow_html=True,
)


# --- Section 1: Pre-Flight Check (Indoor Baseline) ---
st.markdown("### 🏠Indoor Baseline")
st.markdown(
    "<p style='color: #a1a1aa; font-size: 0.9rem; margin-bottom: 20px;'>Your indoor environment dictates your baseline skin state before leaving.</p>",
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-bottom: 20px;'>", unsafe_allow_html=True)
# Determine orb color based on indoor humidity (tradeoff between water retention and oil)
in_hum = indoor_data.get("humidity", 0)
if in_hum > 60:
    core_color = "rgba(245, 158, 11, 0.8)"  # Yellow/Orange: High baseline oil risk
    glow_color = "rgba(245, 158, 11, 0.3)"
    orb_desc = "Optimal Hydration<br>but High Oil Bias"
    orb_badge = "<span class='badge badge-warning'>Oil Risk</span>"
elif in_hum < 30:
    core_color = "rgba(239, 68, 68, 0.8)"  # Red: Too dry
    glow_color = "rgba(239, 68, 68, 0.3)"
    orb_desc = "Critically Dry<br>Low Protection"
    orb_badge = "<span class='badge badge-danger'>Dehydration Alert</span>"
else:
    core_color = "rgba(16, 185, 129, 0.8)"  # Green: Balanced
    glow_color = "rgba(16, 185, 129, 0.3)"
    orb_desc = "Optimal Balance<br>Stable Baseline"
    orb_badge = "<span class='badge badge-success'>Balanced</span>"

orb_html = f"""
<div class='orb-container'>
    <div class='status-orb' style='--core-color: {core_color}; --glow-color: {glow_color}; box-shadow: 0 0 40px {glow_color}, inset 0 0 20px {glow_color};'>
        <div class='orb-ring'></div>
        <div class='orb-text'>{in_hum}%</div>
        <div class='orb-label'>INDOOR HUMIDITY</div>
    </div>
    <div style='text-align: center; margin-top: 24px;'>
        {orb_badge}
        <p style='color: #e4e4e7; margin-top: 8px; font-weight: 500;'>{orb_desc}</p>
    </div>
</div>
"""
st.markdown(orb_html, unsafe_allow_html=True)

# Small metric grid for actual numbers
metrics_html_indoor = f"""
<div class='metric-grid'>
    <div class='metric-box'>
        <div class='metric-val'>{indoor_data.get("temperature", "--")}°C</div>
        <div class='metric-label'>Indoor Temp</div>
    </div>
    <div class='metric-box'>
        <div class='metric-val'>{indoor_data.get("humidity", "--")}%</div>
        <div class='metric-label'>Indoor Humidity</div>
    </div>
</div>
"""
st.markdown(metrics_html_indoor, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# --- Section 2: Step Outside (Environmental Shock) ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown("### 🚪 Step Outside: Environmental Shock")
st.markdown(
    "<p style='color: #a1a1aa; font-size: 0.9rem; margin-bottom: 20px;'>The sudden gap between indoor and outdoor triggers immediate skin reactions.</p>",
    unsafe_allow_html=True,
)

temp_diff = outdoor_data.get("temperature", 0) - indoor_data.get("temperature", 0)
hum_diff = outdoor_data.get("humidity", 0) - indoor_data.get("humidity", 0)

temp_shock_color = "#ef4444" if abs(temp_diff) > 5 else "#10b981"
hum_shock_color = "#3b82f6" if hum_diff > 0 else "#f59e0b"

metrics_html_shock = f"""
<div class='metric-grid'>
    <div class='metric-box' style='border-left: 4px solid {temp_shock_color};'>
        <div class='metric-val' style='color: {temp_shock_color};'>{temp_diff:+.1f}°C</div>
        <div class='metric-label'>Thermal Shock</div>
        <div style='font-size: 0.75rem; color: #71717a; margin-top: 4px;'>Gap between In/Out</div>
    </div>
    <div class='metric-box' style='border-left: 4px solid {hum_shock_color};'>
        <div class='metric-val' style='color: {hum_shock_color};'>{hum_diff:+.1f}%</div>
        <div class='metric-label'>Humidity Shock</div>
        <div style='font-size: 0.75rem; color: #71717a; margin-top: 4px;'>Gap between In/Out</div>
    </div>
</div>
"""
st.markdown(metrics_html_shock, unsafe_allow_html=True)


# --- Section 3: Pure Outdoor Threats ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown("### ☠️ Outdoor Threats")
st.markdown(
    "<p style='color: #a1a1aa; font-size: 0.9rem; margin-bottom: 20px;'>Direct outdoor factors that actively degrade your skin.</p>",
    unsafe_allow_html=True,
)

uv_val = outdoor_data.get("uvIndex", 0)
uv_color = "#ef4444" if uv_val >= 5 else ("#f59e0b" if uv_val >= 3 else "#10b981")
cloud_val = outdoor_data.get("cloudCover", 0)
cloud_color = "#3b82f6" if cloud_val > 70 else "#10b981"

metrics_html_outdoor = f"""
<div class='metric-grid'>
    <div class='metric-box' style='border-left: 4px solid {uv_color};'>
        <div class='metric-val' style='color: {uv_color};'>{uv_val}</div>
        <div class='metric-label'>UV Index</div>
        <div style='font-size: 0.75rem; color: #71717a; margin-top: 4px;'>Primary oil driver</div>
    </div>
    <div class='metric-box' style='border-left: 4px solid {cloud_color};'>
        <div class='metric-val' style='color: {cloud_color};'>{cloud_val}%</div>
        <div class='metric-label'>Cloud Cover</div>
        <div style='font-size: 0.75rem; color: #71717a; margin-top: 4px;'>Water loss driver</div>
    </div>
</div>
"""
st.markdown(metrics_html_outdoor, unsafe_allow_html=True)


# --- Section 4: Action Feed (Going Out Predictor) ---
st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>",
    unsafe_allow_html=True,
)
st.markdown("### 🔔 Recommended Actions")

actions = []

if risk_factors.get("thermal_shock", 0) > 5:
    actions.append(f"""
    <div class='glass-card' style='border-color: rgba(239, 68, 68, 0.3);'>
        <div class='card-title'>⚠️ High Temperature Shock ({risk_factors["thermal_shock"]:.1f}°C jump)</div>
        <div class='card-desc'>Entering a radically hotter environment. Expect slight hydration loss and rapid oil generation. Consider a light, mattifying moisturizer before leaving.</div>
    </div>
    """)

if risk_factors.get("elasticity_boost"):
    actions.append("""
    <div class='glass-card' style='border-color: rgba(16, 185, 129, 0.3);'>
        <div class='card-title'>✨ Elasticity Boost Opportunity</div>
        <div class='card-desc'>Outdoor humidity is currently higher than indoors. Stepping out will give your skin an elasticity boost, though you may generate slightly more oil.</div>
    </div>
    """)

if risk_factors.get("spring_back_risk"):
    actions.append("""
    <div class='glass-card' style='border-color: rgba(59, 130, 246, 0.3);'>
        <div class='card-title'>💧 Rapid 'Spring-Back' Warning</div>
        <div class='card-desc'>Your indoor baseline hydration is high. Stepping outside will cause a rapid loss of moisture due to the spring-back effect. Apply a sealing occlusive layer now.</div>
    </div>
    """)

if risk_factors.get("cloud_risk"):
    actions.append("""
    <div class='glass-card' style='border-color: rgba(96, 165, 250, 0.3);'>
        <div class='card-title'>☁️ Cloud Cover Dehydration</div>
        <div class='card-desc'>Unique data pattern detected: Heavy clouds outside are strongly correlated with dehydration during trips. Pack a hydrating mist.</div>
    </div>
    """)

if risk_factors.get("uv_oil_risk"):
    actions.append(f"""
    <div class='glass-card' style='border-color: rgba(245, 158, 11, 0.3);'>
        <div class='card-title'>☀️ Peak UV Alert (Index: {outdoor_data.get("uvIndex", "--")})</div>
        <div class='card-desc'>High UV exposure outside will rapidly drive up oil production. Apply high SPF and oil-control layer.</div>
    </div>
    """)

if not actions:
    actions.append("""
    <div class='glass-card' style='border-color: rgba(16, 185, 129, 0.3);'>
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
st.markdown("### 📡 2-Hour & 9-Hour Indoor Forecast")
st.markdown(
    "<p style='color: #a1a1aa; font-size: 0.9rem; margin-bottom: 20px;'>How current outdoor conditions will slowly affect your indoor baseline.</p>",
    unsafe_allow_html=True,
)

forecasts = []

if risk_factors.get("wind_crash_forecast"):
    forecasts.append(f"""
    <div class='glass-card' style='border-color: rgba(59, 130, 246, 0.3);'>
        <div class='card-title'>💨 2-Hour Humidity Crash</div>
        <div class='card-desc'>Strong winds detected outside ({outdoor_data.get("windSpeed", 0):.1f} m/s). Your indoor air will become significantly drier within the next 2 hours. We recommend turning on your humidifier now.</div>
    </div>
    """)
else:
    forecasts.append(f"""
    <div class='glass-card'>
        <div class='card-title'>🌬️ 2-Hour Humidity Stable</div>
        <div class='card-desc'>Winds are calm ({outdoor_data.get("windSpeed", 0):.1f} m/s). Indoor humidity should remain stable in the short term.</div>
    </div>
    """)

# Using DewPoint as proxy for thermal lag prediction as per the analysis
dp = outdoor_data.get("dewPoint", 0)
if dp < 5:
    forecasts.append(f"""
    <div class='glass-card'>
        <div class='card-title'>🌡️ 9-Hour Thermal Drift (Cooling)</div>
        <div class='card-desc'>Outdoor dew point drops ({dp}°C). Expect a gradual cooling of your indoor environment over the next 9 hours. This will reduce baseline oil but may dry skin long-term.</div>
    </div>
    """)
else:
    forecasts.append(f"""
    <div class='glass-card'>
        <div class='card-title'>🌡️ 9-Hour Thermal Drift (Warming)</div>
        <div class='card-desc'>Outdoor dew point is high ({dp}°C). The 9-hour thermal lag will push indoor temperatures up, preventing excess baseline oil growth but increasing dehydration risk.</div>
    </div>
    """)

for forecast in forecasts:
    st.markdown(forecast, unsafe_allow_html=True)
