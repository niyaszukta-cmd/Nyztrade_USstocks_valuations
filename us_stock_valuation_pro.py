import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import random
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="US Stock Valuation Pro", 
    page_icon="🇺🇸", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL CSS STYLING - DARK/LIGHT MODE COMPATIBLE
# ============================================================================
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Styles */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main Header - US Theme */
.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    padding: 2.5rem 3rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(26, 35, 126, 0.4);
    position: relative;
    overflow: hidden;
    border-top: 4px solid #ef5350;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

.main-header h1 {
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, #ffffff, #90caf9, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}

.main-header p {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
    color: #e3f2fd;
}

/* Company Header Card - US BLUE THEME */
.company-header {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #2196f3 100%);
    border: none;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 40px rgba(25, 118, 210, 0.35);
    border-left: 5px solid #ef5350;
}

.company-name {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.company-meta {
    display: flex;
    gap: 1rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}

.meta-badge {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
    color: #ffffff !important;
    font-weight: 500;
    border: 1px solid rgba(255,255,255,0.3);
}

/* Fair Value Box - US Blue Theme */
.fair-value-card {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin: 1.5rem 0;
    box-shadow: 0 20px 40px rgba(21, 101, 192, 0.35);
    position: relative;
    overflow: hidden;
}

.fair-value-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(30%, -30%);
}

.fair-value-label {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    opacity: 0.9;
    margin-bottom: 0.5rem;
    color: #ffffff;
}

.fair-value-amount {
    font-size: 3rem;
    font-weight: 700;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
    color: #ffffff;
}

.current-price {
    font-size: 1rem;
    opacity: 0.85;
    color: #ffffff;
}

.upside-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1.5rem;
    border-radius: 30px;
    margin-top: 1rem;
    font-weight: 600;
    font-size: 1.2rem;
    backdrop-filter: blur(10px);
    color: #ffffff;
}

/* Recommendation Boxes */
.rec-container {
    margin: 1.5rem 0;
}

.rec-strong-buy {
    background: linear-gradient(135deg, #2e7d32 0%, #43a047 50%, #66bb6a 100%);
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(46, 125, 50, 0.4);
    position: relative;
    overflow: hidden;
}

.rec-buy {
    background: linear-gradient(135deg, #00838f 0%, #00acc1 50%, #26c6da 100%);
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(0, 131, 143, 0.4);
}

.rec-hold {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 50%, #ffb74d 100%);
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(245, 124, 0, 0.4);
}

.rec-avoid {
    background: linear-gradient(135deg, #c62828 0%, #e53935 50%, #ef5350 100%);
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(198, 40, 40, 0.4);
}

.rec-subtitle {
    font-size: 1rem;
    font-weight: 500;
    opacity: 0.9;
    margin-top: 0.3rem;
    color: white !important;
}

/* Metric Cards - US BLUE THEME */
.metric-card {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
    border: none;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 25px rgba(21, 101, 192, 0.35);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(21, 101, 192, 0.5);
}

.metric-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.85) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}

/* Section Headers - US BLUE THEME */
.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    color: #42a5f5;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #1976d2;
    display: inline-block;
}

/* Sidebar Styling - US BLUE */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d47a1 0%, #1565c0 100%);
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Stock Count Badge - US THEME */
.stock-count {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
    color: white !important;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    text-align: center;
    margin: 1rem 0;
    font-weight: 600;
    border-left: 4px solid #ef5350;
}

/* Valuation Method Cards - US BLUE THEME */
.valuation-method {
    background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #42a5f5;
    box-shadow: 0 8px 25px rgba(13, 71, 161, 0.35);
}

.method-title {
    font-weight: 600;
    color: #ffffff !important;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.method-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.method-label {
    color: rgba(255,255,255,0.7) !important;
}

.method-value {
    font-weight: 600;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Footer - US THEME */
.footer {
    text-align: center;
    padding: 2rem;
    color: #42a5f5;
    font-size: 0.9rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(66, 165, 245, 0.3);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.6s ease forwards;
}

/* Info Box - US BLUE THEME */
.info-box {
    background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
    border: 1px solid #1976d2;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    color: #ffffff !important;
    margin: 1rem 0;
}

.info-box h3 {
    color: #90caf9 !important;
    margin-bottom: 0.5rem;
}

.info-box p, .info-box li {
    color: rgba(255,255,255,0.9) !important;
}

/* Warning Box */
.warning-box {
    background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
    border: 1px solid #f59e0b;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #fef3c7 !important;
    margin: 1rem 0;
}

/* 52 Week Range Card - US BLUE THEME */
.range-card {
    background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(13, 71, 161, 0.35);
}

.range-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.range-low {
    color: #66bb6a;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.range-high {
    color: #ef5350;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.range-bar-container {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    height: 20px;
    position: relative;
    overflow: hidden;
}

.range-bar-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #66bb6a, #ffca28, #ef5350);
}

.range-current {
    text-align: center;
    margin-top: 1rem;
    color: #ffffff;
    font-size: 1.2rem;
    font-weight: 600;
}

.range-current span {
    color: #90caf9;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PASSWORD AUTHENTICATION
# ============================================================================
def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "demo123", "premium": "premium123", "niyas": "nyztrade123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%); 
                    padding: 4rem; border-radius: 24px; text-align: center; margin: 2rem auto; max-width: 500px;
                    box-shadow: 0 25px 50px rgba(13, 71, 161, 0.4); border-top: 5px solid #ef5350;'>
            <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>
                <span style='background: linear-gradient(90deg, #ffffff, #90caf9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    🇺🇸 US Stock Valuation Pro
                </span>
            </h1>
            <p style='color: rgba(255,255,255,0.8); margin-bottom: 2rem;'>Professional US Market Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("👤 Username", key="username", placeholder="Enter username")
            st.text_input("🔒 Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True, type="primary")
            st.info("💡 Demo: demo/demo123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================================
# COMPREHENSIVE US STOCKS DATABASE
# Total Stocks: 1200+ Prominent US Equities
# Organized by: Sector, Industry, and Market Cap
# ============================================================================

US_STOCKS = {
    # ========================================================================
    # 🏆 MEGA CAP - TOP 50 (Market Cap > $200B)
    # ========================================================================
    "🏆 Mega Cap Top 50": {
        "AAPL": "Apple Inc", "MSFT": "Microsoft Corp", "GOOGL": "Alphabet Inc A", "GOOG": "Alphabet Inc C",
        "AMZN": "Amazon.com Inc", "NVDA": "NVIDIA Corp", "META": "Meta Platforms", "TSLA": "Tesla Inc",
        "BRK-B": "Berkshire Hathaway B", "UNH": "UnitedHealth Group", "JNJ": "Johnson & Johnson", "V": "Visa Inc",
        "XOM": "Exxon Mobil", "JPM": "JPMorgan Chase", "WMT": "Walmart Inc", "MA": "Mastercard Inc",
        "PG": "Procter & Gamble", "HD": "Home Depot", "CVX": "Chevron Corp", "LLY": "Eli Lilly",
        "MRK": "Merck & Co", "ABBV": "AbbVie Inc", "PEP": "PepsiCo Inc", "KO": "Coca-Cola Co",
        "COST": "Costco Wholesale", "AVGO": "Broadcom Inc", "TMO": "Thermo Fisher", "MCD": "McDonald's Corp",
        "CSCO": "Cisco Systems", "ACN": "Accenture plc", "ABT": "Abbott Laboratories", "DHR": "Danaher Corp",
        "WFC": "Wells Fargo", "NKE": "Nike Inc", "ADBE": "Adobe Inc", "TXN": "Texas Instruments",
        "CRM": "Salesforce Inc", "NEE": "NextEra Energy", "PM": "Philip Morris", "ORCL": "Oracle Corp",
        "BMY": "Bristol-Myers Squibb", "RTX": "RTX Corp", "UPS": "United Parcel Service", "QCOM": "Qualcomm Inc",
        "HON": "Honeywell Intl", "INTC": "Intel Corp", "IBM": "IBM Corp", "CAT": "Caterpillar Inc",
        "AMGN": "Amgen Inc", "SPGI": "S&P Global"
    },

    # ========================================================================
    # 💻 TECHNOLOGY - Software & Services
    # ========================================================================
    "💻 Tech - Software & Cloud": {
        "CRM": "Salesforce Inc", "NOW": "ServiceNow Inc", "INTU": "Intuit Inc", "PANW": "Palo Alto Networks",
        "SNOW": "Snowflake Inc", "CRWD": "CrowdStrike Holdings", "WDAY": "Workday Inc", "ZS": "Zscaler Inc",
        "DDOG": "Datadog Inc", "NET": "Cloudflare Inc", "MDB": "MongoDB Inc", "TEAM": "Atlassian Corp",
        "HUBS": "HubSpot Inc", "VEEV": "Veeva Systems", "SPLK": "Splunk Inc", "OKTA": "Okta Inc",
        "ZM": "Zoom Video", "DOCU": "DocuSign Inc", "TWLO": "Twilio Inc", "SQ": "Block Inc",
        "SHOP": "Shopify Inc", "U": "Unity Software", "PATH": "UiPath Inc", "CFLT": "Confluent Inc",
        "ESTC": "Elastic NV", "PD": "PagerDuty Inc", "FIVN": "Five9 Inc", "RNG": "RingCentral Inc",
        "ZI": "ZoomInfo Technologies", "BILL": "Bill Holdings", "PCTY": "Paylocity Holding", "PAYC": "Paycom Software",
        "GWRE": "Guidewire Software", "MANH": "Manhattan Associates", "TYL": "Tyler Technologies", "SMAR": "Smartsheet Inc",
        "JAMF": "Jamf Holding", "TENB": "Tenable Holdings", "RPD": "Rapid7 Inc", "SAIL": "SailPoint Technologies"
    },

    "💻 Tech - Semiconductors": {
        "NVDA": "NVIDIA Corp", "AMD": "Advanced Micro Devices", "AVGO": "Broadcom Inc", "QCOM": "Qualcomm Inc",
        "TXN": "Texas Instruments", "INTC": "Intel Corp", "MU": "Micron Technology", "ADI": "Analog Devices",
        "LRCX": "Lam Research", "KLAC": "KLA Corp", "AMAT": "Applied Materials", "MRVL": "Marvell Technology",
        "NXPI": "NXP Semiconductors", "ON": "ON Semiconductor", "MCHP": "Microchip Technology", "SWKS": "Skyworks Solutions",
        "QRVO": "Qorvo Inc", "MPWR": "Monolithic Power", "ENTG": "Entegris Inc", "TER": "Teradyne Inc",
        "LSCC": "Lattice Semiconductor", "SLAB": "Silicon Laboratories", "CRUS": "Cirrus Logic", "MKSI": "MKS Instruments",
        "FORM": "FormFactor Inc", "ACLS": "Axcelis Technologies", "UCTT": "Ultra Clean Holdings", "COHR": "Coherent Corp",
        "WOLF": "Wolfspeed Inc", "RMBS": "Rambus Inc", "SITM": "SiTime Corp", "ALGM": "Allegro MicroSystems",
        "POWI": "Power Integrations", "DIOD": "Diodes Inc", "SMTC": "Semtech Corp", "AOSL": "Alpha & Omega Semi"
    },

    "💻 Tech - Hardware & Equipment": {
        "AAPL": "Apple Inc", "DELL": "Dell Technologies", "HPQ": "HP Inc", "HPE": "Hewlett Packard Enterprise",
        "NTAP": "NetApp Inc", "WDC": "Western Digital", "STX": "Seagate Technology", "PSTG": "Pure Storage",
        "LOGI": "Logitech Intl", "CRSR": "Corsair Gaming", "HEAR": "Turtle Beach Corp", "SMCI": "Super Micro Computer",
        "IONQ": "IonQ Inc", "RGTI": "Rigetti Computing", "QUBT": "Quantum Computing", "BBAI": "BigBear.ai Holdings",
        "ASTS": "AST SpaceMobile", "IRDM": "Iridium Communications", "GSAT": "Globalstar Inc", "GILT": "Gilat Satellite",
        "VIAV": "Viavi Solutions", "LITE": "Lumentum Holdings", "FNSR": "Finisar Corp", "CIEN": "Ciena Corp",
        "INFN": "Infinera Corp", "COMM": "CommScope Holding", "CALX": "Calix Inc", "ADTN": "Adtran Holdings",
        "EXTR": "Extreme Networks", "CAMP": "CalAmp Corp", "GILT": "Gilat Satellite", "VIAV": "Viavi Solutions"
    },

    "💻 Tech - IT Services": {
        "ACN": "Accenture plc", "IBM": "IBM Corp", "CTSH": "Cognizant Technology", "INFY": "Infosys Ltd",
        "WIT": "Wipro Ltd", "EPAM": "EPAM Systems", "GLOB": "Globant SA", "DXC": "DXC Technology",
        "LDOS": "Leidos Holdings", "BAH": "Booz Allen Hamilton", "CACI": "CACI International", "SAIC": "Science Applications",
        "KBR": "KBR Inc", "MANT": "ManTech International", "ICFI": "ICF International", "PRFT": "Perficient Inc",
        "EXLS": "ExlService Holdings", "WNS": "WNS Holdings", "TTEC": "TTEC Holdings", "CNXC": "Concentrix Corp",
        "TASK": "TaskUs Inc", "GDS": "GDS Holdings", "VNT": "Vontier Corp", "BR": "Broadridge Financial"
    },

    # ========================================================================
    # 🏦 FINANCIAL SERVICES
    # ========================================================================
    "🏦 Banks - Large Cap": {
        "JPM": "JPMorgan Chase", "BAC": "Bank of America", "WFC": "Wells Fargo", "C": "Citigroup Inc",
        "GS": "Goldman Sachs", "MS": "Morgan Stanley", "USB": "US Bancorp", "PNC": "PNC Financial",
        "TFC": "Truist Financial", "SCHW": "Charles Schwab", "BK": "Bank of New York Mellon", "STT": "State Street Corp",
        "COF": "Capital One Financial", "AXP": "American Express", "DFS": "Discover Financial", "SYF": "Synchrony Financial",
        "ALLY": "Ally Financial", "CFG": "Citizens Financial", "MTB": "M&T Bank Corp", "FITB": "Fifth Third Bancorp",
        "HBAN": "Huntington Bancshares", "KEY": "KeyCorp", "RF": "Regions Financial", "ZION": "Zions Bancorp",
        "CMA": "Comerica Inc", "FRC": "First Republic Bank", "SIVB": "SVB Financial Group", "FHN": "First Horizon",
        "EWBC": "East West Bancorp", "WBS": "Webster Financial", "BOKF": "BOK Financial", "GBCI": "Glacier Bancorp"
    },

    "🏦 Banks - Regional": {
        "FCNCA": "First Citizens BancShares", "PNFP": "Pinnacle Financial", "UMBF": "UMB Financial",
        "FNB": "FNB Corp", "ONB": "Old National Bancorp", "CBSH": "Commerce Bancshares", "WTFC": "Wintrust Financial",
        "SBCF": "Seacoast Banking", "FFIN": "First Financial Bankshares", "BANF": "BancFirst Corp", "TCBI": "Texas Capital",
        "HWC": "Hancock Whitney", "SFBS": "ServisFirst Bancshares", "CADE": "Cadence Bank", "IBOC": "International Bancshares",
        "WAFD": "WaFd Inc", "NWBI": "Northwest Bancshares", "ABCB": "Ameris Bancorp", "TOWN": "TowneBank",
        "UCBI": "United Community Banks", "CVBF": "CVB Financial", "WSFS": "WSFS Financial", "PACW": "PacWest Bancorp",
        "WAL": "Western Alliance", "COLB": "Columbia Banking", "BANR": "Banner Bank", "FIBK": "First Interstate",
        "TRMK": "Trustmark Corp", "FULT": "Fulton Financial", "BHLB": "Berkshire Hills", "ASB": "Associated Banc-Corp"
    },

    "🏦 Asset Management & Custody": {
        "BLK": "BlackRock Inc", "BX": "Blackstone Inc", "KKR": "KKR & Co", "APO": "Apollo Global",
        "CG": "Carlyle Group", "ARES": "Ares Management", "OWL": "Blue Owl Capital", "TPG": "TPG Inc",
        "TROW": "T Rowe Price", "IVZ": "Invesco Ltd", "BEN": "Franklin Resources", "NTRS": "Northern Trust",
        "AMG": "Affiliated Managers", "JHG": "Janus Henderson", "VRTS": "Virtus Investment", "FHI": "Federated Hermes",
        "VCTR": "Victory Capital", "CNS": "Cohen & Steers", "AB": "AllianceBernstein", "EV": "Eaton Vance",
        "WDR": "Waddell & Reed", "APAM": "Artisan Partners", "HLNE": "Hamilton Lane", "STEP": "StepStone Group"
    },

    "🏦 Insurance - Life & Health": {
        "MET": "MetLife Inc", "PRU": "Prudential Financial", "AFL": "Aflac Inc", "LNC": "Lincoln National",
        "PFG": "Principal Financial", "VOYA": "Voya Financial", "UNM": "Unum Group", "GL": "Globe Life",
        "BHF": "Brighthouse Financial", "EQH": "Equitable Holdings", "ATH": "Athene Holding", "RGA": "Reinsurance Group",
        "CNO": "CNO Financial", "FAF": "First American Financial", "FNF": "Fidelity National Financial"
    },

    "🏦 Insurance - Property & Casualty": {
        "BRK-B": "Berkshire Hathaway B", "PGR": "Progressive Corp", "TRV": "Travelers Companies", "CB": "Chubb Ltd",
        "ALL": "Allstate Corp", "HIG": "Hartford Financial", "CNA": "CNA Financial", "WRB": "WR Berkley",
        "CINF": "Cincinnati Financial", "L": "Loews Corp", "MKL": "Markel Corp", "AFG": "American Financial",
        "RE": "Everest Re Group", "RNR": "RenaissanceRe", "ACGL": "Arch Capital", "AXS": "Axis Capital",
        "ORI": "Old Republic Intl", "THG": "Hanover Insurance", "SIGI": "Selective Insurance", "KMPR": "Kemper Corp",
        "KNSL": "Kinsale Capital", "PLMR": "Palomar Holdings", "HCI": "HCI Group", "RYAN": "Ryan Specialty"
    },

    "🏦 Financial Technology": {
        "V": "Visa Inc", "MA": "Mastercard Inc", "PYPL": "PayPal Holdings", "SQ": "Block Inc",
        "FIS": "Fidelity National Info", "FISV": "Fiserv Inc", "GPN": "Global Payments", "ADP": "Automatic Data Processing",
        "PAYX": "Paychex Inc", "FLT": "FleetCor Technologies", "WEX": "WEX Inc", "JKHY": "Jack Henry & Associates",
        "AFRM": "Affirm Holdings", "UPST": "Upstart Holdings", "SOFI": "SoFi Technologies", "LC": "LendingClub Corp",
        "TOST": "Toast Inc", "FOUR": "Shift4 Payments", "PAYO": "Payoneer Global", "NUVEI": "Nuvei Corp",
        "EVTC": "Evertec Inc", "RPAY": "Repay Holdings", "PSFE": "Paysafe Ltd", "OLO": "Olo Inc",
        "RELY": "Remitly Global", "DLO": "DLocal Ltd", "NU": "Nu Holdings", "COIN": "Coinbase Global",
        "HOOD": "Robinhood Markets", "MKTX": "MarketAxess Holdings", "TW": "Tradeweb Markets", "NDAQ": "Nasdaq Inc"
    },

    # ========================================================================
    # 🏥 HEALTHCARE
    # ========================================================================
    "🏥 Healthcare - Pharma Large Cap": {
        "JNJ": "Johnson & Johnson", "LLY": "Eli Lilly", "PFE": "Pfizer Inc", "MRK": "Merck & Co",
        "ABBV": "AbbVie Inc", "BMY": "Bristol-Myers Squibb", "AMGN": "Amgen Inc", "GILD": "Gilead Sciences",
        "REGN": "Regeneron Pharma", "VRTX": "Vertex Pharma", "BIIB": "Biogen Inc", "MRNA": "Moderna Inc",
        "AZN": "AstraZeneca", "NVS": "Novartis AG", "GSK": "GSK plc", "SNY": "Sanofi SA",
        "NVO": "Novo Nordisk", "ZTS": "Zoetis Inc", "CTLT": "Catalent Inc", "CRL": "Charles River Labs"
    },

    "🏥 Healthcare - Biotech": {
        "VRTX": "Vertex Pharma", "REGN": "Regeneron Pharma", "BIIB": "Biogen Inc", "MRNA": "Moderna Inc",
        "SGEN": "Seagen Inc", "ALNY": "Alnylam Pharma", "INCY": "Incyte Corp", "BMRN": "BioMarin Pharma",
        "SRPT": "Sarepta Therapeutics", "IONS": "Ionis Pharma", "NBIX": "Neurocrine Biosciences", "EXEL": "Exelixis Inc",
        "HZNP": "Horizon Therapeutics", "UTHR": "United Therapeutics", "TECH": "Bio-Techne Corp", "BGNE": "BeiGene Ltd",
        "RARE": "Ultragenyx Pharma", "FOLD": "Amicus Therapeutics", "BLUE": "Bluebird Bio", "ARCT": "Arcturus Therapeutics",
        "FATE": "Fate Therapeutics", "CRSP": "CRISPR Therapeutics", "EDIT": "Editas Medicine", "NTLA": "Intellia Therapeutics",
        "BEAM": "Beam Therapeutics", "VCNX": "Vaccinex Inc", "SANA": "Sana Biotechnology", "VERV": "Verve Therapeutics",
        "RCKT": "Rocket Pharma", "DCPH": "Deciphera Pharma", "KYMR": "Kymera Therapeutics", "RVMD": "Revolution Medicines"
    },

    "🏥 Healthcare - Medical Devices": {
        "ABT": "Abbott Laboratories", "MDT": "Medtronic plc", "SYK": "Stryker Corp", "BSX": "Boston Scientific",
        "EW": "Edwards Lifesciences", "ISRG": "Intuitive Surgical", "BDX": "Becton Dickinson", "ZBH": "Zimmer Biomet",
        "DXCM": "DexCom Inc", "PODD": "Insulet Corp", "HOLX": "Hologic Inc", "BAX": "Baxter International",
        "ALGN": "Align Technology", "IDXX": "IDEXX Laboratories", "TFX": "Teleflex Inc", "INSP": "Inspire Medical",
        "NVST": "Envista Holdings", "XRAY": "Dentsply Sirona", "RMD": "ResMed Inc", "AMED": "Amedisys Inc",
        "GMED": "Globus Medical", "MMSI": "Merit Medical", "NUVA": "NuVasive Inc", "LIVN": "LivaNova plc",
        "NVCR": "NovoCure Ltd", "AXNX": "Axonics Inc", "TNDM": "Tandem Diabetes", "SWAV": "Shockwave Medical",
        "HSKA": "Heska Corp", "ICUI": "ICU Medical", "PRCT": "Procept BioRobotics", "SILK": "Silk Road Medical"
    },

    "🏥 Healthcare - Services & Facilities": {
        "UNH": "UnitedHealth Group", "ELV": "Elevance Health", "CI": "Cigna Group", "HUM": "Humana Inc",
        "CNC": "Centene Corp", "MOH": "Molina Healthcare", "HCA": "HCA Healthcare", "UHS": "Universal Health Services",
        "THC": "Tenet Healthcare", "ACHC": "Acadia Healthcare", "EHC": "Encompass Health", "DVA": "DaVita Inc",
        "ENSG": "Ensign Group", "NHC": "National HealthCare", "SEM": "Select Medical", "SGRY": "Surgery Partners",
        "ALHC": "Alignment Healthcare", "OSH": "Oak Street Health", "AGL": "agilon health", "OSCR": "Oscar Health",
        "CLOV": "Clover Health", "TALK": "Talkspace Inc", "HIMS": "Hims & Hers Health", "DOCS": "Doximity Inc",
        "TDOC": "Teladoc Health", "AMWL": "Amwell Corp", "ONEM": "1Life Healthcare", "ACCD": "Accolade Inc"
    },

    "🏥 Healthcare - Distributors & Services": {
        "MCK": "McKesson Corp", "ABC": "AmerisourceBergen", "CAH": "Cardinal Health", "OMI": "Owens & Minor",
        "HSIC": "Henry Schein", "PDCO": "Patterson Companies", "COO": "Cooper Companies", "TECH": "Bio-Techne",
        "PKI": "PerkinElmer", "A": "Agilent Technologies", "WAT": "Waters Corp", "MTD": "Mettler-Toledo",
        "TMO": "Thermo Fisher", "DHR": "Danaher Corp", "IQV": "IQVIA Holdings", "MEDP": "Medpace Holdings",
        "ICLR": "ICON plc", "PPD": "PPD Inc", "SYNH": "Syneos Health", "PRA": "PRA Health Sciences"
    },

    # ========================================================================
    # 🛒 CONSUMER - Discretionary
    # ========================================================================
    "🛒 Consumer - Retail": {
        "AMZN": "Amazon.com Inc", "WMT": "Walmart Inc", "COST": "Costco Wholesale", "TGT": "Target Corp",
        "HD": "Home Depot", "LOW": "Lowe's Companies", "TJX": "TJX Companies", "ROST": "Ross Stores",
        "BURL": "Burlington Stores", "DG": "Dollar General", "DLTR": "Dollar Tree", "FIVE": "Five Below",
        "ULTA": "Ulta Beauty", "BBY": "Best Buy Co", "WSM": "Williams-Sonoma", "RH": "RH Inc",
        "ETSY": "Etsy Inc", "W": "Wayfair Inc", "CHWY": "Chewy Inc", "CVNA": "Carvana Co",
        "KMX": "CarMax Inc", "AN": "AutoNation Inc", "PAG": "Penske Automotive", "LAD": "Lithia Motors",
        "GPC": "Genuine Parts", "AAP": "Advance Auto Parts", "ORLY": "O'Reilly Automotive", "AZO": "AutoZone Inc",
        "TSCO": "Tractor Supply", "OLLI": "Ollie's Bargain", "BIG": "Big Lots Inc", "PRTY": "Party City"
    },

    "🛒 Consumer - E-Commerce & Internet": {
        "AMZN": "Amazon.com Inc", "BABA": "Alibaba Group", "JD": "JD.com Inc", "PDD": "PDD Holdings",
        "MELI": "MercadoLibre Inc", "SE": "Sea Limited", "CPNG": "Coupang Inc", "EBAY": "eBay Inc",
        "ETSY": "Etsy Inc", "W": "Wayfair Inc", "CHWY": "Chewy Inc", "WISH": "ContextLogic Inc",
        "RVLV": "Revolve Group", "REAL": "RealReal Inc", "POSH": "Poshmark Inc", "FTCH": "Farfetch Ltd",
        "BIGC": "BigCommerce Holdings", "SHOP": "Shopify Inc", "WIX": "Wix.com Ltd", "GDDY": "GoDaddy Inc",
        "YELP": "Yelp Inc", "TRIP": "TripAdvisor Inc", "BKNG": "Booking Holdings", "EXPE": "Expedia Group",
        "ABNB": "Airbnb Inc", "DASH": "DoorDash Inc", "UBER": "Uber Technologies", "LYFT": "Lyft Inc"
    },

    "🛒 Consumer - Restaurants": {
        "MCD": "McDonald's Corp", "SBUX": "Starbucks Corp", "CMG": "Chipotle Mexican Grill", "YUM": "Yum! Brands",
        "DPZ": "Domino's Pizza", "QSR": "Restaurant Brands", "DNUT": "Krispy Kreme", "WEN": "Wendy's Co",
        "DRI": "Darden Restaurants", "TXRH": "Texas Roadhouse", "EAT": "Brinker International", "BLMN": "Bloomin' Brands",
        "CAKE": "Cheesecake Factory", "BJRI": "BJ's Restaurants", "DIN": "Dine Brands", "JACK": "Jack in the Box",
        "SHAK": "Shake Shack Inc", "WING": "Wingstop Inc", "PLAY": "Dave & Buster's", "PZZA": "Papa John's",
        "BROS": "Dutch Bros Inc", "CAVA": "CAVA Group", "SWEETGREEN": "Sweetgreen Inc", "PTLO": "Portillo's Inc",
        "ARMK": "Aramark", "USFD": "US Foods Holding", "SYY": "Sysco Corp", "PFGC": "Performance Food Group"
    },

    "🛒 Consumer - Apparel & Luxury": {
        "NKE": "Nike Inc", "LULU": "Lululemon Athletica", "UAA": "Under Armour A", "UA": "Under Armour C",
        "VFC": "VF Corp", "PVH": "PVH Corp", "RL": "Ralph Lauren", "TPR": "Tapestry Inc",
        "CPRI": "Capri Holdings", "GPS": "Gap Inc", "ANF": "Abercrombie & Fitch", "AEO": "American Eagle",
        "URBN": "Urban Outfitters", "EXPR": "Express Inc", "GOOS": "Canada Goose", "BOOT": "Boot Barn Holdings",
        "DECK": "Deckers Outdoor", "SKX": "Skechers USA", "CROX": "Crocs Inc", "WWW": "Wolverine World Wide",
        "FL": "Foot Locker", "HIBB": "Hibbett Inc", "FINL": "Finish Line", "DKS": "Dick's Sporting Goods",
        "ASO": "Academy Sports", "BGFV": "Big 5 Sporting", "GIII": "G-III Apparel", "OXM": "Oxford Industries"
    },

    "🛒 Consumer - Entertainment & Leisure": {
        "DIS": "Walt Disney Co", "NFLX": "Netflix Inc", "CMCSA": "Comcast Corp", "WBD": "Warner Bros Discovery",
        "PARA": "Paramount Global", "LYV": "Live Nation Entertainment", "MSGS": "Madison Square Garden Sports",
        "MSGE": "Madison Square Garden Entertainment", "WWE": "World Wrestling Entertainment", "EDR": "Endeavor Group",
        "SPOT": "Spotify Technology", "TME": "Tencent Music", "SONO": "Sonos Inc", "ROKU": "Roku Inc",
        "FUBO": "fuboTV Inc", "AMC": "AMC Entertainment", "CNK": "Cinemark Holdings", "IMAX": "IMAX Corp",
        "SIX": "Six Flags Entertainment", "FUN": "Cedar Fair", "SEAS": "SeaWorld Entertainment", "MTN": "Vail Resorts",
        "SKI": "Boyne Resorts", "HLT": "Hilton Worldwide", "MAR": "Marriott International", "H": "Hyatt Hotels",
        "WH": "Wyndham Hotels", "CHH": "Choice Hotels", "IHG": "InterContinental Hotels", "ABNB": "Airbnb Inc"
    },

    "🛒 Consumer - Automotive": {
        "TSLA": "Tesla Inc", "F": "Ford Motor Co", "GM": "General Motors", "STLA": "Stellantis NV",
        "RIVN": "Rivian Automotive", "LCID": "Lucid Group", "FSR": "Fisker Inc", "NIO": "NIO Inc",
        "XPEV": "XPeng Inc", "LI": "Li Auto Inc", "GOEV": "Canoo Inc", "WKHS": "Workhorse Group",
        "RIDE": "Lordstown Motors", "NKLA": "Nikola Corp", "HYLN": "Hyliion Holdings", "PTRA": "Proterra Inc",
        "LEA": "Lear Corp", "BWA": "BorgWarner Inc", "APTV": "Aptiv plc", "ALV": "Autoliv Inc",
        "MGA": "Magna International", "VC": "Visteon Corp", "DAN": "Dana Inc", "ADNT": "Adient plc",
        "AXL": "American Axle", "GNTX": "Gentex Corp", "MOD": "Modine Manufacturing", "SMP": "Standard Motor Products"
    },

    # ========================================================================
    # 🍔 CONSUMER STAPLES
    # ========================================================================
    "🍔 Consumer Staples - Food & Beverage": {
        "PEP": "PepsiCo Inc", "KO": "Coca-Cola Co", "MDLZ": "Mondelez International", "GIS": "General Mills",
        "K": "Kellogg Co", "CPB": "Campbell Soup", "SJM": "JM Smucker", "CAG": "Conagra Brands",
        "HSY": "Hershey Co", "MKC": "McCormick & Co", "HRL": "Hormel Foods", "TSN": "Tyson Foods",
        "BG": "Bunge Ltd", "ADM": "Archer-Daniels-Midland", "INGR": "Ingredion Inc", "DAR": "Darling Ingredients",
        "KHC": "Kraft Heinz Co", "LANC": "Lancaster Colony", "POST": "Post Holdings", "THS": "TreeHouse Foods",
        "BGS": "B&G Foods", "LNDC": "Landec Corp", "JJSF": "J&J Snack Foods", "FRPT": "Freshpet Inc",
        "BYND": "Beyond Meat", "OTLY": "Oatly Group", "TTCF": "Tattooed Chef", "BRCC": "BRC Inc"
    },

    "🍔 Consumer Staples - Beverages": {
        "KO": "Coca-Cola Co", "PEP": "PepsiCo Inc", "KDP": "Keurig Dr Pepper", "MNST": "Monster Beverage",
        "CELH": "Celsius Holdings", "STZ": "Constellation Brands", "BF-B": "Brown-Forman B", "BF-A": "Brown-Forman A",
        "DEO": "Diageo plc", "SAM": "Boston Beer Co", "TAP": "Molson Coors B", "CCU": "Compania Cervecerias",
        "FIZZ": "National Beverage", "COKE": "Coca-Cola Consolidated", "PRMW": "Primo Water", "WVVI": "Willamette Valley"
    },

    "🍔 Consumer Staples - Household & Personal": {
        "PG": "Procter & Gamble", "CL": "Colgate-Palmolive", "KMB": "Kimberly-Clark", "CHD": "Church & Dwight",
        "CLX": "Clorox Co", "SPB": "Spectrum Brands", "EL": "Estee Lauder", "COTY": "Coty Inc",
        "ELF": "e.l.f. Beauty", "ULTA": "Ulta Beauty", "REV": "Revlon Inc", "SBH": "Sally Beauty",
        "IPAR": "Inter Parfums", "NUS": "Nu Skin Enterprises", "USNA": "USANA Health", "PRGO": "Perrigo Co",
        "HELE": "Helen of Troy", "ENR": "Energizer Holdings", "HNST": "Honest Company", "BJ": "BJ's Wholesale"
    },

    "🍔 Consumer Staples - Retail & Tobacco": {
        "WMT": "Walmart Inc", "COST": "Costco Wholesale", "KR": "Kroger Co", "WBA": "Walgreens Boots Alliance",
        "CVS": "CVS Health Corp", "TGT": "Target Corp", "SYY": "Sysco Corp", "ACI": "Albertsons Cos",
        "GO": "Grocery Outlet", "SFM": "Sprouts Farmers Market", "NGVC": "Natural Grocers", "UNFI": "United Natural Foods",
        "PM": "Philip Morris", "MO": "Altria Group", "BTI": "British American Tobacco", "IMBBY": "Imperial Brands",
        "TPB": "Turning Point Brands", "NJDCY": "Japan Tobacco", "VGR": "Vector Group", "CSWI": "CSW Industrials"
    },

    # ========================================================================
    # ⚡ ENERGY
    # ========================================================================
    "⚡ Energy - Oil & Gas Majors": {
        "XOM": "Exxon Mobil", "CVX": "Chevron Corp", "COP": "ConocoPhillips", "EOG": "EOG Resources",
        "SLB": "Schlumberger Ltd", "PXD": "Pioneer Natural Resources", "MPC": "Marathon Petroleum", "PSX": "Phillips 66",
        "VLO": "Valero Energy", "OXY": "Occidental Petroleum", "DVN": "Devon Energy", "HES": "Hess Corp",
        "FANG": "Diamondback Energy", "MRO": "Marathon Oil", "APA": "APA Corp", "OVV": "Ovintiv Inc",
        "CTRA": "Coterra Energy", "EQT": "EQT Corp", "AR": "Antero Resources", "RRC": "Range Resources",
        "SWN": "Southwestern Energy", "CNX": "CNX Resources", "CHK": "Chesapeake Energy", "MTDR": "Matador Resources"
    },

    "⚡ Energy - Oil Services & Equipment": {
        "SLB": "Schlumberger Ltd", "HAL": "Halliburton Co", "BKR": "Baker Hughes Co", "NOV": "NOV Inc",
        "FTI": "TechnipFMC plc", "CHX": "ChampionX Corp", "WFRD": "Weatherford Intl", "HP": "Helmerich & Payne",
        "PTEN": "Patterson-UTI Energy", "NBR": "Nabors Industries", "RIG": "Transocean Ltd", "VAL": "Valaris Ltd",
        "NE": "Noble Corp", "DO": "Diamond Offshore", "BORR": "Borr Drilling", "PDS": "Precision Drilling",
        "DRQ": "Dril-Quip Inc", "OII": "Oceaneering Intl", "LBRT": "Liberty Energy", "PUMP": "ProPetro Holding",
        "NINE": "Nine Energy Service", "WTTR": "Select Water Solutions", "TUSK": "Mammoth Energy", "USAC": "USA Compression"
    },

    "⚡ Energy - Midstream & MLPs": {
        "WMB": "Williams Companies", "KMI": "Kinder Morgan", "OKE": "ONEOK Inc", "EPD": "Enterprise Products",
        "ET": "Energy Transfer LP", "MPLX": "MPLX LP", "PAA": "Plains All American", "TRGP": "Targa Resources",
        "LNG": "Cheniere Energy", "DTM": "DT Midstream", "AM": "Antero Midstream", "ENLC": "EnLink Midstream",
        "WES": "Western Midstream", "HESM": "Hess Midstream", "CTRA": "Coterra Energy", "NFG": "National Fuel Gas",
        "DCP": "DCP Midstream", "CEQP": "Crestwood Equity", "SMLP": "Summit Midstream", "USAC": "USA Compression"
    },

    "⚡ Energy - Renewable & Clean": {
        "NEE": "NextEra Energy", "ENPH": "Enphase Energy", "SEDG": "SolarEdge Technologies", "FSLR": "First Solar",
        "RUN": "Sunrun Inc", "NOVA": "Sunnova Energy", "SPWR": "SunPower Corp", "JKS": "JinkoSolar Holding",
        "CSIQ": "Canadian Solar", "DQ": "Daqo New Energy", "MAXN": "Maxeon Solar", "ARRY": "Array Technologies",
        "SHLS": "Shoals Technologies", "STEM": "Stem Inc", "BE": "Bloom Energy", "PLUG": "Plug Power",
        "BLDP": "Ballard Power", "FCEL": "FuelCell Energy", "CLNE": "Clean Energy Fuels", "CHPT": "ChargePoint Holdings",
        "BLNK": "Blink Charging", "EVGO": "EVgo Inc", "DCFC": "Tritium DCFC", "PTRA": "Proterra Inc"
    },

    # ========================================================================
    # 🏭 INDUSTRIALS
    # ========================================================================
    "🏭 Industrials - Aerospace & Defense": {
        "BA": "Boeing Co", "LMT": "Lockheed Martin", "RTX": "RTX Corp", "NOC": "Northrop Grumman",
        "GD": "General Dynamics", "LHX": "L3Harris Technologies", "TDG": "TransDigm Group", "HWM": "Howmet Aerospace",
        "TXT": "Textron Inc", "HII": "Huntington Ingalls", "AXON": "Axon Enterprise", "KTOS": "Kratos Defense",
        "MRCY": "Mercury Systems", "AVAV": "AeroVironment Inc", "RKLB": "Rocket Lab USA", "SPCE": "Virgin Galactic",
        "ASTR": "Astra Space", "RDW": "Redwire Corp", "MNTS": "Momentus Inc", "ASTS": "AST SpaceMobile",
        "HEI": "HEICO Corp", "HEI-A": "HEICO Corp A", "AIR": "AAR Corp", "CW": "Curtiss-Wright",
        "MOG-A": "Moog Inc A", "SPR": "Spirit AeroSystems", "WWD": "Woodward Inc", "DCO": "Ducommun Inc"
    },

    "🏭 Industrials - Machinery & Equipment": {
        "CAT": "Caterpillar Inc", "DE": "Deere & Co", "CNHI": "CNH Industrial", "AGCO": "AGCO Corp",
        "CMI": "Cummins Inc", "PH": "Parker-Hannifin", "EMR": "Emerson Electric", "ROK": "Rockwell Automation",
        "ETN": "Eaton Corp", "DOV": "Dover Corp", "ITW": "Illinois Tool Works", "SWK": "Stanley Black & Decker",
        "FAST": "Fastenal Co", "GWW": "WW Grainger", "WSO": "Watsco Inc", "TTC": "Toro Co",
        "OSK": "Oshkosh Corp", "TEX": "Terex Corp", "GNRC": "Generac Holdings", "XYL": "Xylem Inc",
        "IEX": "IDEX Corp", "NDSN": "Nordson Corp", "GGG": "Graco Inc", "FLS": "Flowserve Corp",
        "AME": "AMETEK Inc", "RBC": "RBC Bearings", "ROLL": "RBC Bearings", "TRS": "TriMas Corp"
    },

    "🏭 Industrials - Transportation": {
        "UNP": "Union Pacific Corp", "CSX": "CSX Corp", "NSC": "Norfolk Southern", "CNI": "Canadian National Railway",
        "CP": "Canadian Pacific Kansas City", "KSU": "Kansas City Southern", "JBHT": "JB Hunt Transport",
        "XPO": "XPO Inc", "ODFL": "Old Dominion Freight", "SAIA": "Saia Inc", "CHRW": "CH Robinson Worldwide",
        "EXPD": "Expeditors International", "UPS": "United Parcel Service", "FDX": "FedEx Corp", "UBER": "Uber Technologies",
        "LYFT": "Lyft Inc", "DAL": "Delta Air Lines", "UAL": "United Airlines Holdings", "AAL": "American Airlines",
        "LUV": "Southwest Airlines", "ALK": "Alaska Air Group", "JBLU": "JetBlue Airways", "SAVE": "Spirit Airlines",
        "HA": "Hawaiian Holdings", "SKYW": "SkyWest Inc", "MESA": "Mesa Air Group", "ATSG": "Air Transport Services"
    },

    "🏭 Industrials - Building & Construction": {
        "SHW": "Sherwin-Williams", "PPG": "PPG Industries", "APD": "Air Products & Chemicals", "ECL": "Ecolab Inc",
        "VMC": "Vulcan Materials", "MLM": "Martin Marietta", "EXP": "Eagle Materials", "SUM": "Summit Materials",
        "USCR": "US Concrete", "CRH": "CRH plc", "CX": "CEMEX SAB", "MAS": "Masco Corp",
        "OC": "Owens Corning", "BLDR": "Builders FirstSource", "BLD": "TopBuild Corp", "AZEK": "AZEK Co",
        "TREX": "Trex Co", "AWI": "Armstrong World Industries", "DOOR": "Masonite International", "JELD": "JELD-WEN Holding",
        "LPX": "Louisiana-Pacific", "BECN": "Beacon Roofing", "GMS": "GMS Inc", "TILE": "Interface Inc",
        "FBK": "FB Financial", "APOG": "Apogee Enterprises", "ROCK": "Gibraltar Industries", "PRIM": "Primoris Services"
    },

    "🏭 Industrials - Conglomerates & Diversified": {
        "HON": "Honeywell Intl", "MMM": "3M Co", "GE": "GE Aerospace", "JCI": "Johnson Controls",
        "IR": "Ingersoll Rand", "ROP": "Roper Technologies", "ITT": "ITT Inc", "PNR": "Pentair plc",
        "AOS": "AO Smith Corp", "WTS": "Watts Water Technologies", "CFX": "Colfax Corp", "FTV": "Fortive Corp",
        "DHR": "Danaher Corp", "CARR": "Carrier Global", "OTIS": "Otis Worldwide", "TT": "Trane Technologies",
        "LII": "Lennox International", "WCC": "WESCO International", "RXN": "Rexnord Corp", "ALLE": "Allegion plc"
    },

    # ========================================================================
    # 🏠 REAL ESTATE
    # ========================================================================
    "🏠 REITs - Diversified & Office": {
        "PLD": "Prologis Inc", "AMT": "American Tower Corp", "CCI": "Crown Castle Intl", "EQIX": "Equinix Inc",
        "DLR": "Digital Realty Trust", "PSA": "Public Storage", "SPG": "Simon Property Group", "WELL": "Welltower Inc",
        "AVB": "AvalonBay Communities", "EQR": "Equity Residential", "VTR": "Ventas Inc", "O": "Realty Income Corp",
        "BXP": "Boston Properties", "ARE": "Alexandria Real Estate", "SLG": "SL Green Realty", "VNO": "Vornado Realty",
        "KIM": "Kimco Realty", "REG": "Regency Centers", "FRT": "Federal Realty Investment", "HST": "Host Hotels & Resorts",
        "RHP": "Ryman Hospitality", "PK": "Park Hotels & Resorts", "SHO": "Sunstone Hotel", "DRH": "DiamondRock Hospitality"
    },

    "🏠 REITs - Residential": {
        "EQR": "Equity Residential", "AVB": "AvalonBay Communities", "ESS": "Essex Property Trust", "UDR": "UDR Inc",
        "MAA": "Mid-America Apartment", "CPT": "Camden Property Trust", "AIV": "Apartment Investment", "NXRT": "NexPoint Residential",
        "IRT": "Independence Realty", "ELME": "Elme Communities", "VRE": "Veris Residential", "CSR": "Centerspace",
        "INVH": "Invitation Homes", "AMH": "American Homes 4 Rent", "SUI": "Sun Communities", "ELS": "Equity LifeStyle",
        "UMH": "UMH Properties", "NNN": "NNN REIT", "ADC": "Agree Realty", "STOR": "STORE Capital"
    },

    "🏠 REITs - Industrial & Data Centers": {
        "PLD": "Prologis Inc", "DRE": "Duke Realty", "REXR": "Rexford Industrial", "FR": "First Industrial Realty",
        "EGP": "EastGroup Properties", "STAG": "STAG Industrial", "TRNO": "Terreno Realty", "COLD": "Americold Realty",
        "DLR": "Digital Realty Trust", "EQIX": "Equinix Inc", "AMT": "American Tower Corp", "CCI": "Crown Castle Intl",
        "SBAC": "SBA Communications", "UNIT": "Uniti Group", "CONE": "CyrusOne Inc", "QTS": "QTS Realty Trust",
        "VNET": "VNET Group", "GDS": "GDS Holdings", "CORZ": "Core Scientific", "MARA": "Marathon Digital"
    },

    "🏠 REITs - Retail & Specialty": {
        "SPG": "Simon Property Group", "MAC": "Macerich Co", "SKT": "Tanger Factory Outlet", "PEI": "Pennsylvania REIT",
        "CBL": "CBL & Associates", "WPG": "Washington Prime", "KIM": "Kimco Realty", "REG": "Regency Centers",
        "FRT": "Federal Realty Investment", "BRX": "Brixmor Property", "ROIC": "Retail Opportunity", "SITC": "SITE Centers",
        "RPT": "RPT Realty", "AKR": "Acadia Realty", "UE": "Urban Edge Properties", "RPAI": "Retail Properties",
        "WRI": "Weingarten Realty", "KRG": "Kite Realty Group", "PINE": "Alpine Income Property", "GTY": "Getty Realty"
    },

    # ========================================================================
    # 📡 COMMUNICATION SERVICES
    # ========================================================================
    "📡 Communication - Telecom": {
        "T": "AT&T Inc", "VZ": "Verizon Communications", "TMUS": "T-Mobile US", "CHTR": "Charter Communications",
        "CMCSA": "Comcast Corp", "LUMN": "Lumen Technologies", "FYBR": "Frontier Communications", "USM": "US Cellular",
        "TDS": "Telephone & Data Systems", "SHEN": "Shenandoah Telecom", "LILA": "Liberty Latin America A",
        "LILAK": "Liberty Latin America K", "CABO": "Cable One", "CCOI": "Cogent Communications", "BAND": "Bandwidth Inc",
        "IRDM": "Iridium Communications", "GSAT": "Globalstar Inc", "VSAT": "Viasat Inc", "SATS": "EchoStar Corp"
    },

    "📡 Communication - Media & Entertainment": {
        "DIS": "Walt Disney Co", "NFLX": "Netflix Inc", "WBD": "Warner Bros Discovery", "PARA": "Paramount Global",
        "FOXA": "Fox Corp A", "FOX": "Fox Corp B", "VIAC": "ViacomCBS", "DISCA": "Discovery A", "DISCB": "Discovery B",
        "DISCK": "Discovery C", "AMCX": "AMC Networks", "CNXC": "Concentrix Corp", "IPG": "Interpublic Group",
        "OMC": "Omnicom Group", "WPP": "WPP plc", "PUBM": "PubMatic Inc", "MGNI": "Magnite Inc",
        "TTD": "Trade Desk", "APPS": "Digital Turbine", "ZNGA": "Zynga Inc", "EA": "Electronic Arts",
        "TTWO": "Take-Two Interactive", "ATVI": "Activision Blizzard", "RBLX": "Roblox Corp", "U": "Unity Software"
    },

    "📡 Communication - Internet & Social Media": {
        "GOOGL": "Alphabet Inc A", "GOOG": "Alphabet Inc C", "META": "Meta Platforms", "SNAP": "Snap Inc",
        "PINS": "Pinterest Inc", "TWTR": "Twitter Inc", "MTCH": "Match Group", "BMBL": "Bumble Inc",
        "ZG": "Zillow Group C", "Z": "Zillow Group A", "RDFN": "Redfin Corp", "OPEN": "Opendoor Technologies",
        "COUR": "Coursera Inc", "DUOL": "Duolingo Inc", "CHGG": "Chegg Inc", "UDMY": "Udemy Inc",
        "SKIL": "Skillsoft Corp", "LRN": "Stride Inc", "PRDO": "Perdoceo Education", "STRA": "Strategic Education"
    },

    # ========================================================================
    # 🔧 MATERIALS
    # ========================================================================
    "🔧 Materials - Chemicals": {
        "LIN": "Linde plc", "APD": "Air Products & Chemicals", "SHW": "Sherwin-Williams", "ECL": "Ecolab Inc",
        "DD": "DuPont de Nemours", "DOW": "Dow Inc", "LYB": "LyondellBasell", "PPG": "PPG Industries",
        "NUE": "Nucor Corp", "ALB": "Albemarle Corp", "EMN": "Eastman Chemical", "CE": "Celanese Corp",
        "FMC": "FMC Corp", "IFF": "International Flavors", "CTVA": "Corteva Inc", "CF": "CF Industries",
        "MOS": "Mosaic Co", "NTR": "Nutrien Ltd", "SMG": "Scotts Miracle-Gro", "ICL": "ICL Group",
        "CC": "Chemours Co", "AXTA": "Axalta Coating", "RPM": "RPM International", "ASH": "Ashland Global",
        "HUN": "Huntsman Corp", "OLN": "Olin Corp", "WLK": "Westlake Corp", "TROX": "Tronox Holdings"
    },

    "🔧 Materials - Metals & Mining": {
        "NUE": "Nucor Corp", "STLD": "Steel Dynamics", "CLF": "Cleveland-Cliffs", "X": "United States Steel",
        "CMC": "Commercial Metals", "RS": "Reliance Steel", "ATI": "ATI Inc", "HAYN": "Haynes International",
        "CRS": "Carpenter Technology", "ZEUS": "Olympic Steel", "SCHN": "Schnitzer Steel", "AA": "Alcoa Corp",
        "CENX": "Century Aluminum", "KALU": "Kaiser Aluminum", "ARNC": "Arconic Corp", "HCC": "Warrior Met Coal",
        "ARCH": "Arch Resources", "AMR": "Alpha Metallurgical", "CEIX": "CONSOL Energy", "BTU": "Peabody Energy",
        "FCX": "Freeport-McMoRan", "SCCO": "Southern Copper", "TECK": "Teck Resources", "RIO": "Rio Tinto",
        "BHP": "BHP Group", "VALE": "Vale SA", "NEM": "Newmont Corp", "GOLD": "Barrick Gold",
        "AEM": "Agnico Eagle Mines", "KGC": "Kinross Gold", "AU": "AngloGold Ashanti", "HMY": "Harmony Gold"
    },

    "🔧 Materials - Paper & Packaging": {
        "IP": "International Paper", "PKG": "Packaging Corp of America", "WRK": "WestRock Co", "GPK": "Graphic Packaging",
        "SLGN": "Silgan Holdings", "SON": "Sonoco Products", "SEE": "Sealed Air Corp", "BLL": "Ball Corp",
        "CCK": "Crown Holdings", "ATR": "AptarGroup Inc", "BERY": "Berry Global", "AMCR": "Amcor plc",
        "PTVE": "Pactiv Evergreen", "GEF": "Greif Inc", "CLW": "Clearwater Paper", "MERC": "Mercer International",
        "RYAM": "Rayonier Advanced", "KS": "Kapstone Paper", "UFS": "Domtar Corp", "RYN": "Rayonier Inc"
    },

    # ========================================================================
    # ⚙️ UTILITIES
    # ========================================================================
    "⚙️ Utilities - Electric": {
        "NEE": "NextEra Energy", "DUK": "Duke Energy", "SO": "Southern Co", "D": "Dominion Energy",
        "AEP": "American Electric Power", "SRE": "Sempra Energy", "EXC": "Exelon Corp", "XEL": "Xcel Energy",
        "ED": "Consolidated Edison", "PEG": "Public Service Enterprise", "WEC": "WEC Energy Group", "ES": "Eversource Energy",
        "EIX": "Edison International", "AWK": "American Water Works", "ETR": "Entergy Corp", "FE": "FirstEnergy Corp",
        "DTE": "DTE Energy", "AEE": "Ameren Corp", "CMS": "CMS Energy", "CNP": "CenterPoint Energy",
        "PPL": "PPL Corp", "EVRG": "Evergy Inc", "AES": "AES Corp", "NI": "NiSource Inc",
        "LNT": "Alliant Energy", "OGE": "OGE Energy", "PNW": "Pinnacle West Capital", "NRG": "NRG Energy"
    },

    "⚙️ Utilities - Gas & Water": {
        "SRE": "Sempra Energy", "NI": "NiSource Inc", "ATO": "Atmos Energy", "OGS": "ONE Gas Inc",
        "NJR": "New Jersey Resources", "NFG": "National Fuel Gas", "SWX": "Southwest Gas", "RGCO": "RGC Resources",
        "AWK": "American Water Works", "WTRG": "Essential Utilities", "AWR": "American States Water", "CWT": "California Water",
        "SJW": "SJW Group", "YORW": "York Water Co", "MSEX": "Middlesex Water", "ARTNA": "Artesian Resources"
    },

    # ========================================================================
    # 🎰 GAMING & CANNABIS
    # ========================================================================
    "🎰 Gaming & Casinos": {
        "LVS": "Las Vegas Sands", "WYNN": "Wynn Resorts", "MGM": "MGM Resorts", "CZR": "Caesars Entertainment",
        "MLCO": "Melco Resorts", "PENN": "Penn Entertainment", "BYD": "Boyd Gaming", "RRR": "Red Rock Resorts",
        "GDEN": "Golden Entertainment", "CHDN": "Churchill Downs", "DKNG": "DraftKings Inc", "FLUT": "Flutter Entertainment",
        "RSI": "Rush Street Interactive", "BALY": "Bally's Corp", "GNOG": "Golden Nugget Online", "AGS": "PlayAGS",
        "IGT": "International Game Technology", "SGMS": "Scientific Games", "EVRI": "Everi Holdings", "ACEL": "Accel Entertainment"
    },

    "🌿 Cannabis & CBD": {
        "TLRY": "Tilray Brands", "CGC": "Canopy Growth", "ACB": "Aurora Cannabis", "CRON": "Cronos Group",
        "HEXO": "HEXO Corp", "OGI": "Organigram Holdings", "SNDL": "SNDL Inc", "VFF": "Village Farms",
        "GRWG": "GrowGeneration Corp", "HYFM": "Hydrofarm Holdings", "SMG": "Scotts Miracle-Gro", "IIPR": "Innovative Industrial",
        "CURLF": "Curaleaf Holdings", "GTBIF": "Green Thumb Industries", "TCNNF": "Trulieve Cannabis", "CRLBF": "Cresco Labs"
    },

    # ========================================================================
    # 🔬 EMERGING TECH & INNOVATION
    # ========================================================================
    "🔬 AI & Machine Learning": {
        "NVDA": "NVIDIA Corp", "GOOGL": "Alphabet Inc A", "MSFT": "Microsoft Corp", "META": "Meta Platforms",
        "AMZN": "Amazon.com Inc", "IBM": "IBM Corp", "PLTR": "Palantir Technologies", "AI": "C3.ai Inc",
        "UPST": "Upstart Holdings", "PATH": "UiPath Inc", "BBAI": "BigBear.ai Holdings", "SOUN": "SoundHound AI",
        "GFAI": "Guardforce AI", "AITX": "Artificial Intelligence Technology", "VCNX": "Vaccinex Inc"
    },

    "🔬 Cybersecurity": {
        "PANW": "Palo Alto Networks", "CRWD": "CrowdStrike Holdings", "ZS": "Zscaler Inc", "FTNT": "Fortinet Inc",
        "OKTA": "Okta Inc", "NET": "Cloudflare Inc", "S": "SentinelOne Inc", "TENB": "Tenable Holdings",
        "RPD": "Rapid7 Inc", "CYBR": "CyberArk Software", "VRNS": "Varonis Systems", "SAIL": "SailPoint Technologies",
        "QLYS": "Qualys Inc", "PFPT": "Proofpoint Inc", "FEYE": "FireEye Inc", "MIME": "Mimecast Ltd",
        "RDWR": "Radware Ltd", "CHKP": "Check Point Software", "NLOK": "NortonLifeLock", "AVGO": "Broadcom Inc"
    },

    "🔬 Blockchain & Crypto": {
        "COIN": "Coinbase Global", "MARA": "Marathon Digital", "RIOT": "Riot Platforms", "HUT": "Hut 8 Mining",
        "BITF": "Bitfarms Ltd", "CLSK": "CleanSpark Inc", "BTBT": "Bit Digital", "CORZ": "Core Scientific",
        "CIFR": "Cipher Mining", "IREN": "Iris Energy", "SQ": "Block Inc", "PYPL": "PayPal Holdings",
        "MSTR": "MicroStrategy Inc", "GBTC": "Grayscale Bitcoin Trust", "ETHE": "Grayscale Ethereum Trust",
        "SI": "Silvergate Capital", "SBNY": "Signature Bank", "HOOD": "Robinhood Markets"
    },

    "🔬 Space & Aerospace Tech": {
        "RKLB": "Rocket Lab USA", "SPCE": "Virgin Galactic", "ASTR": "Astra Space", "RDW": "Redwire Corp",
        "MNTS": "Momentus Inc", "ASTS": "AST SpaceMobile", "BKSY": "BlackSky Technology", "PL": "Planet Labs",
        "LLAP": "Terran Orbital", "VORB": "Virgin Orbit", "SATX": "SatixFy Communications", "IRDM": "Iridium Communications",
        "GSAT": "Globalstar Inc", "VSAT": "Viasat Inc", "SATS": "EchoStar Corp"
    },

    # ========================================================================
    # 📊 ETFs & INDEX TRACKING (Popular for Reference)
    # ========================================================================
    "📊 Major ETFs": {
        "SPY": "SPDR S&P 500 ETF", "QQQ": "Invesco QQQ Trust", "IWM": "iShares Russell 2000", "DIA": "SPDR Dow Jones",
        "VOO": "Vanguard S&P 500", "VTI": "Vanguard Total Stock Market", "IVV": "iShares Core S&P 500", "VEA": "Vanguard FTSE Developed",
        "EFA": "iShares MSCI EAFE", "VWO": "Vanguard FTSE Emerging Markets", "EEM": "iShares MSCI Emerging Markets",
        "GLD": "SPDR Gold Shares", "SLV": "iShares Silver Trust", "TLT": "iShares 20+ Year Treasury", "HYG": "iShares High Yield Corporate",
        "LQD": "iShares Investment Grade Corporate", "XLF": "Financial Select Sector SPDR", "XLK": "Technology Select Sector SPDR",
        "XLE": "Energy Select Sector SPDR", "XLV": "Health Care Select Sector SPDR", "XLI": "Industrial Select Sector SPDR",
        "XLY": "Consumer Discretionary Select Sector SPDR", "XLP": "Consumer Staples Select Sector SPDR", "XLRE": "Real Estate Select Sector SPDR",
        "XLB": "Materials Select Sector SPDR", "XLU": "Utilities Select Sector SPDR", "XLC": "Communication Services Select Sector SPDR",
        "ARKK": "ARK Innovation ETF", "ARKG": "ARK Genomic Revolution ETF", "ARKW": "ARK Next Generation Internet ETF"
    }
}

# ============================================================================
# INDUSTRY BENCHMARKS - US MARKETS
# ============================================================================

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 28, 'ev_ebitda': 18, 'ps': 8},
    'Financial Services': {'pe': 14, 'ev_ebitda': 10, 'ps': 3},
    'Healthcare': {'pe': 22, 'ev_ebitda': 14, 'ps': 4},
    'Consumer Cyclical': {'pe': 25, 'ev_ebitda': 12, 'ps': 2},
    'Consumer Defensive': {'pe': 22, 'ev_ebitda': 14, 'ps': 2},
    'Industrials': {'pe': 20, 'ev_ebitda': 12, 'ps': 2},
    'Energy': {'pe': 12, 'ev_ebitda': 6, 'ps': 1},
    'Basic Materials': {'pe': 15, 'ev_ebitda': 8, 'ps': 1.5},
    'Real Estate': {'pe': 35, 'ev_ebitda': 18, 'ps': 8},
    'Communication Services': {'pe': 18, 'ev_ebitda': 10, 'ps': 3},
    'Utilities': {'pe': 18, 'ev_ebitda': 10, 'ps': 2},
    'Default': {'pe': 20, 'ev_ebitda': 12, 'ps': 3}
}

# Sector-specific growth benchmarks
GROWTH_BENCHMARKS = {
    'Technology': {'revenue_growth': 15, 'earnings_growth': 18},
    'Healthcare': {'revenue_growth': 8, 'earnings_growth': 12},
    'Financial Services': {'revenue_growth': 5, 'earnings_growth': 8},
    'Consumer Cyclical': {'revenue_growth': 8, 'earnings_growth': 10},
    'Consumer Defensive': {'revenue_growth': 4, 'earnings_growth': 6},
    'Industrials': {'revenue_growth': 6, 'earnings_growth': 8},
    'Energy': {'revenue_growth': 5, 'earnings_growth': 10},
    'Default': {'revenue_growth': 6, 'earnings_growth': 8}
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_stocks():
    """Returns a flat dictionary of all stocks with their names"""
    all_stocks = {}
    for category, stocks in US_STOCKS.items():
        all_stocks.update(stocks)
    return all_stocks

def get_stock_count():
    """Returns total count of unique stocks"""
    return len(get_all_stocks())

def get_categories():
    """Returns list of all categories"""
    return list(US_STOCKS.keys())

def search_stock(query):
    """Search for stocks by ticker or name"""
    query = query.upper()
    results = {}
    for category, stocks in US_STOCKS.items():
        for ticker, name in stocks.items():
            if query in ticker.upper() or query in name.upper():
                results[ticker] = {'name': name, 'category': category}
    return results

def get_stocks_by_category(category_keyword):
    """Get stocks from categories matching keyword"""
    results = {}
    for category, stocks in US_STOCKS.items():
        if category_keyword.lower() in category.lower():
            results[category] = stocks
    return results

def get_stocks_by_sector(sector):
    """Get all stocks in a specific sector"""
    sector_mapping = {
        'technology': ['Tech', 'Software', 'Semiconductor', 'Hardware', 'IT Services', 'AI', 'Cybersecurity'],
        'healthcare': ['Healthcare', 'Pharma', 'Biotech', 'Medical'],
        'financial': ['Bank', 'Insurance', 'Asset Management', 'Financial'],
        'consumer': ['Consumer', 'Retail', 'Restaurant', 'Apparel', 'Entertainment'],
        'industrial': ['Industrial', 'Aerospace', 'Machinery', 'Transportation', 'Building'],
        'energy': ['Energy', 'Oil', 'Renewable'],
        'materials': ['Materials', 'Chemical', 'Metal', 'Mining', 'Paper'],
        'realestate': ['REIT', 'Real Estate'],
        'communication': ['Communication', 'Telecom', 'Media', 'Internet'],
        'utilities': ['Utilities', 'Electric', 'Gas', 'Water']
    }
    
    keywords = sector_mapping.get(sector.lower(), [])
    results = {}
    for category, stocks in US_STOCKS.items():
        for keyword in keywords:
            if keyword.lower() in category.lower():
                results.update(stocks)
                break
    return results

def get_benchmark(sector):
    """Get benchmark PE and EV/EBITDA for a sector"""
    return INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS.get('Default'))

# ============================================================================
# MARKET CAP CLASSIFICATION
# ============================================================================

MARKET_CAP_TIERS = {
    'Mega Cap': 200_000_000_000,      # > $200B
    'Large Cap': 10_000_000_000,       # $10B - $200B
    'Mid Cap': 2_000_000_000,          # $2B - $10B
    'Small Cap': 300_000_000,          # $300M - $2B
    'Micro Cap': 0                      # < $300M
}

# ============================================================================
# QUICK STATS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("US STOCKS DATABASE - COMPREHENSIVE SUMMARY")
    print("=" * 70)
    print(f"Total Categories: {len(get_categories())}")
    print(f"Total Unique Stocks: {get_stock_count()}")
    print("-" * 70)
    print("\nCategories Breakdown:")
    for cat in get_categories():
        count = len(US_STOCKS[cat])
        print(f"  {cat}: {count} stocks")
    print("=" * 70)
# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def retry_with_backoff(retries=5, backoff_in_seconds=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

# Session-level cache to avoid repeated calls
if 'stock_cache' not in st.session_state:
    st.session_state.stock_cache = {}
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

def fetch_stock_data_direct(ticker):
    """Fetch stock data using yfinance with rate limit handling"""
    try:
        # Ensure minimum delay between requests (3-6 seconds random)
        current_time = time.time()
        time_since_last = current_time - st.session_state.last_request_time
        min_delay = 3 + random.random() * 3  # 3-6 seconds
        
        if time_since_last < min_delay:
            time.sleep(min_delay - time_since_last)
        
        st.session_state.last_request_time = time.time()
        
        # Create ticker - use default session (no custom session)
        stock = yf.Ticker(ticker)
        
        # Try to get info
        info = stock.info
            
        if not info or len(info) < 5:
            return None, "Unable to fetch data - ticker may be invalid"
        
        # Check if we got valid data
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or info.get('previousClose', 0)
        if not price or price <= 0:
            return None, "No price data available for this ticker"
            
        return info, None
        
   except Exception as e:
        error_msg = str(e).lower()
        if "429" in str(e) or "rate" in error_msg or "too many" in error_msg or "limited" in error_msg:
            return None, "RATE_LIMIT"
        if "expecting value" in error_msg or "jsondecodeerror" in error_msg:
            return None, "RATE_LIMIT"
        if "no data" in error_msg or "not found" in error_msg or "404" in str(e):
            return None, f"Ticker '{ticker}' not found"
        if "connection" in error_msg or "timeout" in error_msg:
            return None, "Connection error - please try again"
        return None, f"Error: {str(e)[:60]}"

@st.cache_data(ttl=21600, show_spinner=False)  # 6-hour cache
def fetch_stock_cached(ticker):
    """Cached version of stock fetch"""
    return fetch_stock_data_direct(ticker)

def fetch_with_session_cache(ticker):
    """Wrapper that uses session cache first, then disk cache"""
    # Check session cache first (valid for current session)
    cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d')}"
    
    if cache_key in st.session_state.stock_cache:
        cached_data = st.session_state.stock_cache[cache_key]
        if cached_data[0] is not None:  # Only return if we have valid data
            return cached_data
    
    # Try cached fetch
    result = fetch_stock_cached(ticker)
    
    # Store in session cache if successful
    if result[0] is not None:
        st.session_state.stock_cache[cache_key] = result
    
    return result

def calculate_valuations(info):
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        sector = info.get('sector', 'Default')
        book_value = info.get('bookValue', 0)
        revenue = info.get('totalRevenue', 0)
        
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        # PE-based valuation
        historical_pe = trailing_pe * 0.9 if trailing_pe and trailing_pe > 0 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # EV/EBITDA-based valuation
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2 if current_ev_ebitda and 0 < current_ev_ebitda < 50 else industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Price to Book valuation
        pb_ratio = price / book_value if book_value and book_value > 0 else None
        
        # Price to Sales
        ps_ratio = market_cap / revenue if revenue and revenue > 0 else None
        
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,
            'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,
            'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev,
            'pb_ratio': pb_ratio, 'ps_ratio': ps_ratio,
            'book_value': book_value, 'revenue': revenue,
            'net_debt': (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'roe': info.get('returnOnEquity', 0),
            'profit_margin': info.get('profitMargins', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
        }
    except:
        return None

# ============================================================================
# PROFESSIONAL CHART FUNCTIONS
# ============================================================================
def create_gauge_chart(upside_pe, upside_ev):
    """Create professional dual gauge chart for valuations"""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        horizontal_spacing=0.15
    )
    
    # PE Multiple Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe if upside_pe else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Multiple", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': '#e2e8f0'}
    )
    return fig

def create_valuation_comparison_chart(vals):
    """Create professional bar chart comparing current vs fair values"""
    categories = []
    current_vals = []
    fair_vals = []
    
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_pe'])
    
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_ev'])
    
    if not categories:
        return None
    
    fig = go.Figure()
    
    # Current Price bars
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current_vals,
        marker=dict(
            color='#1976d2',
            line=dict(color='#42a5f5', width=2),
        ),
        text=[f'${v:,.2f}' for v in current_vals],
        textposition='outside',
        textfont=dict(size=14, color='#e2e8f0', family='JetBrains Mono')
    ))
    
    # Fair Value bars
    colors = ['#66bb6a' if fv > cv else '#ef5350' for fv, cv in zip(fair_vals, current_vals)]
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair_vals,
        marker=dict(
            color=colors,
            line=dict(color=['#81c784' if c == '#66bb6a' else '#e57373' for c in colors], width=2),
        ),
        text=[f'${v:,.2f}' for v in fair_vals],
        textposition='outside',
        textfont=dict(size=14, color='#e2e8f0', family='JetBrains Mono')
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12, color='#e2e8f0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color='#e2e8f0')
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#4c1d95',
            tickfont=dict(size=14, color='#e2e8f0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(167, 139, 250, 0.2)',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=12, color='#a78bfa')
        ),
        margin=dict(l=60, r=40, t=60, b=40)
    )
    
    return fig

def create_52week_range_display(vals):
    """Create 52-week price range display using HTML/CSS instead of Plotly"""
    low = vals.get('52w_low', 0)
    high = vals.get('52w_high', 0)
    current = vals.get('price', 0)
    
    if not all([low, high, current]) or high <= low:
        return None
    
    # Calculate position percentage
    position = ((current - low) / (high - low)) * 100
    position = max(0, min(100, position))  # Clamp between 0-100
    
    html = f'''
    <div class="range-card">
        <div class="range-header">
            <div class="range-low">52W Low: ${low:,.2f}</div>
            <div class="range-high">52W High: ${high:,.2f}</div>
        </div>
        <div class="range-bar-container">
            <div class="range-bar-fill" style="width: {position}%;"></div>
        </div>
        <div class="range-current">
            Current Price: <span>${current:,.2f}</span> ({position:.1f}% of range)
        </div>
    </div>
    '''
    return html

def create_radar_chart(vals):
    """Create radar chart for key metrics comparison"""
    categories = ['PE Ratio', 'EV/EBITDA', 'P/B Ratio', 'Profit Margin', 'ROE']
    
    # Normalize values (0-100 scale)
    pe_score = max(0, min(100, 100 - (vals['trailing_pe'] / vals['industry_pe'] * 50))) if vals['trailing_pe'] and vals['industry_pe'] else 50
    ev_score = max(0, min(100, 100 - (vals['current_ev_ebitda'] / vals['industry_ev_ebitda'] * 50))) if vals['current_ev_ebitda'] and vals['industry_ev_ebitda'] else 50
    pb_score = max(0, min(100, 100 - (vals['pb_ratio'] * 20))) if vals['pb_ratio'] else 50
    margin_score = vals['profit_margin'] * 500 if vals['profit_margin'] else 50
    roe_score = vals['roe'] * 300 if vals['roe'] else 50
    
    values = [pe_score, ev_score, pb_score, margin_score, roe_score]
    values = [max(0, min(100, v)) for v in values]  # Clamp values
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(124, 58, 237, 0.3)',
        line=dict(color='#a78bfa', width=2),
        marker=dict(size=8, color='#c4b5fd')
    ))
    
    # Add benchmark line
    fig.add_trace(go.Scatterpolar(
        r=[50, 50, 50, 50, 50, 50],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='#6366f1', width=2, dash='dash'),
        name='Benchmark'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='rgba(167, 139, 250, 0.2)',
                linecolor='rgba(167, 139, 250, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#a78bfa'),
                linecolor='rgba(167, 139, 250, 0.3)',
                gridcolor='rgba(167, 139, 250, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        height=350,
        margin=dict(l=60, r=60, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0')
    )
    
    return fig

# ============================================================================
# PDF REPORT GENERATION
# ============================================================================
def create_pdf_report(company, ticker, sector, vals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=28, 
        textColor=colors.HexColor('#1565c0'), 
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph("US Stock Valuation Pro", title_style))
    story.append(Paragraph("Professional Valuation Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Company Info
    story.append(Paragraph(f"<b>{company}</b>", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Calculate averages
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Fair Value Summary
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value', f"$ {avg_fair:,.2f}"],
        ['Current Price', f"$ {vals['price']:,.2f}"],
        ['Potential Upside', f"{avg_up:+.2f}%"]
    ]
    fair_table = Table(fair_data, colWidths=[3*inch, 2.5*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#90caf9')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 25))
    
    # Detailed Metrics
    story.append(Paragraph("<b>Valuation Metrics</b>", styles['Heading3']))
    metrics_data = [
        ['Metric', 'Current', 'Industry Benchmark'],
        ['PE Ratio', f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A', f"{vals['industry_pe']:.2f}x"],
        ['EV/EBITDA', f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A', f"{vals['industry_ev_ebitda']:.2f}x"],
        ['P/B Ratio', f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else 'N/A', '-'],
        ['EPS', f"$ {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A', '-'],
        ['Market Cap', f"$ {vals['market_cap']/1000000000:,.2f}B", '-'],
    ]
    metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        spaceBefore=20
    )
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> This report is for educational purposes only and does not constitute financial advice. "
        "Always consult a qualified financial advisor before making investment decisions. Past performance is not "
        "indicative of future results.",
        disclaimer_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Header
st.markdown('''
<div class="main-header">
    <h1>🇺🇸 US STOCK VALUATION PRO</h1>
    <p>📊 1,200+ Stocks | NYSE & NASDAQ | Professional Multi-Factor Analysis</p>
</div>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔐 Account")
    st.markdown(f"**User:** {st.session_state.get('authenticated_user', 'Guest').title()}")
    
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 Stock Selection")
    
    # Aggregate all stocks
    all_stocks = {}
    for cat, stocks in US_STOCKS.items():
        all_stocks.update(stocks)
    
    st.markdown(f'''
    <div class="stock-count">
        📊 {len(all_stocks):,} Stocks Available
    </div>
    ''', unsafe_allow_html=True)
    
    # Category selection
    category = st.selectbox(
        "🏷️ Category",
        ["📋 All Stocks"] + list(US_STOCKS.keys()),
        help="Filter stocks by category"
    )
    
    # Search
    search = st.text_input(
        "🔍 Search",
        placeholder="Company name or ticker...",
        help="Search by company name or ticker symbol"
    )
    
    # Filter stocks
    if search:
        search_upper = search.upper()
        filtered = {t: n for t, n in all_stocks.items() 
                   if search_upper in t.upper() or search_upper in n.upper()}
    elif category == "📋 All Stocks":
        filtered = all_stocks
    else:
        filtered = US_STOCKS.get(category, {})
    
    # Stock selection
    if filtered:
        options = sorted([f"{n} ({t})" for t, n in filtered.items()])
        selected = st.selectbox(
            "🎯 Select Stock",
            options,
            help="Choose a stock to analyze"
        )
        ticker = selected.split("(")[1].strip(")")
    else:
        ticker = None
        st.warning("⚠️ No stocks found matching your criteria")
    
    # Custom ticker
    st.markdown("---")
    custom = st.text_input(
        "✏️ Custom Ticker",
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter any US stock ticker manually"
    )
    
    # Analyze button
    st.markdown("---")
    analyze_clicked = st.button("🚀 ANALYZE STOCK", use_container_width=True, type="primary")
    
    # Rate limit info
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; font-size: 0.75rem;'>
        <strong>💡 Tips:</strong><br>
        • Data is cached for 4 hours<br>
        • Wait 1-2 min between requests<br>
        • If rate limited, try again later
    </div>
    """, unsafe_allow_html=True)

# Main content
if analyze_clicked:
    st.session_state.analyze = custom.upper() if custom else ticker

if 'analyze' in st.session_state and st.session_state.analyze:
    t = st.session_state.analyze
    
    # Fetch data with progress and rate limit awareness
    with st.spinner(f"🔄 Fetching data for {t}... This may take a few seconds"):
        info, error = fetch_with_session_cache(t)
    
    if error or not info:
        if error == "RATE_LIMIT":
            st.error("⏳ Yahoo Finance Rate Limit - Please wait and retry")
            st.markdown('''
            <div class="warning-box">
                <strong>⏳ Rate Limit Reached</strong><br>
                Yahoo Finance has temporarily limited requests from this server.<br><br>
                <strong>Solutions:</strong><br>
                • Click the <strong>Retry</strong> button below after waiting 30-60 seconds<br>
                • The app caches successful requests for 6 hours<br>
                • Try during off-peak hours (early morning US time)
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Retry Now", use_container_width=True, type="primary"):
                    # Clear the cache for this ticker and retry
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.error(f"❌ Error: {error}")
            st.markdown('''
            <div class="warning-box">
                <strong>Troubleshooting Tips:</strong><br>
                • Verify the ticker symbol is correct (e.g., AAPL, MSFT, GOOGL)<br>
                • Some tickers like BRK-B may need special formatting (try BRK-B or BRK.B)<br>
                • Check your internet connection<br>
                • Try again in a few moments
            </div>
            ''', unsafe_allow_html=True)
        st.stop()
    
    vals = calculate_valuations(info)
    if not vals:
        st.error("❌ Unable to calculate valuations for this stock")
        st.stop()
    
    # Extract company info
    company = info.get('longName', t)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    # Company Header - FIXED VISIBILITY
    st.markdown(f'''
    <div class="company-header">
        <h2 class="company-name">{company}</h2>
        <div class="company-meta">
            <span class="meta-badge">🏷️ {t}</span>
            <span class="meta-badge">🏢 {sector}</span>
            <span class="meta-badge">🏭 {industry}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Calculate average values
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Main metrics row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Fair Value Card
        st.markdown(f'''
        <div class="fair-value-card">
            <div class="fair-value-label">📊 Calculated Fair Value</div>
            <div class="fair-value-amount">${avg_fair:,.2f}</div>
            <div class="current-price">Current Price: ${vals["price"]:,.2f}</div>
            <div class="upside-badge">{"📈" if avg_up > 0 else "📉"} {avg_up:+.2f}% Potential</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Recommendation
        if avg_up > 25:
            rec_class, rec_text, rec_icon = "rec-strong-buy", "STRONG BUY", "🚀"
        elif avg_up > 15:
            rec_class, rec_text, rec_icon = "rec-buy", "BUY", "✅"
        elif avg_up > 0:
            rec_class, rec_text, rec_icon = "rec-buy", "ACCUMULATE", "📥"
        elif avg_up > -10:
            rec_class, rec_text, rec_icon = "rec-hold", "HOLD", "⏸️"
        else:
            rec_class, rec_text, rec_icon = "rec-avoid", "AVOID", "⚠️"
        
        st.markdown(f'''
        <div class="rec-container">
            <div class="{rec_class}">
                {rec_icon} {rec_text}
                <div class="rec-subtitle">Expected Return: {avg_up:+.2f}%</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # PDF Download
        pdf = create_pdf_report(company, t, sector, vals)
        st.download_button(
            "📥 Download PDF Report",
            data=pdf,
            file_name=f"USStock_{t}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Key Metrics Cards
    st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">${vals['price']:,.2f}</div>
            <div class="metric-label">Current Price</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m2:
        pe_val = f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">{pe_val}</div>
            <div class="metric-label">PE Ratio</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m3:
        eps_val = f"${vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">💵</div>
            <div class="metric-value">{eps_val}</div>
            <div class="metric-label">EPS (TTM)</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m4:
        mcap_val = f"${vals['market_cap']/1000000000:,.1f}B"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">🏦</div>
            <div class="metric-value">{mcap_val}</div>
            <div class="metric-label">Market Cap</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m5:
        ev_ebitda = f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{ev_ebitda}</div>
            <div class="metric-label">EV/EBITDA</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m6:
        pb_val = f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📚</div>
            <div class="metric-value">{pb_val}</div>
            <div class="metric-label">P/B Ratio</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="section-header">🎯 Valuation Gauges</div>', unsafe_allow_html=True)
        if vals['upside_pe'] is not None or vals['upside_ev'] is not None:
            fig_gauge = create_gauge_chart(
                vals['upside_pe'] if vals['upside_pe'] else 0,
                vals['upside_ev'] if vals['upside_ev'] else 0
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("Insufficient data for gauge charts")
    
    with chart_col2:
        st.markdown('<div class="section-header">📊 Price vs Fair Value</div>', unsafe_allow_html=True)
        fig_bar = create_valuation_comparison_chart(vals)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Insufficient data for comparison chart")
    
    # Additional Charts Row
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="section-header">📍 52-Week Range</div>', unsafe_allow_html=True)
        range_html = create_52week_range_display(vals)
        if range_html:
            st.markdown(range_html, unsafe_allow_html=True)
        else:
            st.info("52-week data not available")
    
    with chart_col4:
        st.markdown('<div class="section-header">🎯 Metrics Radar</div>', unsafe_allow_html=True)
        fig_radar = create_radar_chart(vals)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed Valuation Methods
    st.markdown("---")
    st.markdown('<div class="section-header">📋 Valuation Breakdown</div>', unsafe_allow_html=True)
    
    val_col1, val_col2 = st.columns(2)
    
    with val_col1:
        if vals['fair_value_pe'] and vals['trailing_pe']:
            upside_color = '#66bb6a' if vals['upside_pe'] and vals['upside_pe'] > 0 else '#ef5350'
            fair_color = '#66bb6a' if vals['fair_value_pe'] > vals['price'] else '#ef5350'
            st.markdown(f'''
            <div class="valuation-method">
                <div class="method-title">📈 PE Multiple Method</div>
                <div class="method-row">
                    <span class="method-label">Current PE</span>
                    <span class="method-value">{vals['trailing_pe']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Industry PE</span>
                    <span class="method-value">{vals['industry_pe']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">EPS (TTM)</span>
                    <span class="method-value">${vals['trailing_eps']:.2f}</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Fair Value (PE)</span>
                    <span class="method-value" style="color: {fair_color}">${vals['fair_value_pe']:,.2f}</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Upside (PE)</span>
                    <span class="method-value" style="color: {upside_color}">{vals['upside_pe']:+.2f}%</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("PE valuation not available")
    
    with val_col2:
        if vals['fair_value_ev'] and vals['current_ev_ebitda']:
            upside_color_ev = '#66bb6a' if vals['upside_ev'] and vals['upside_ev'] > 0 else '#ef5350'
            fair_color_ev = '#66bb6a' if vals['fair_value_ev'] > vals['price'] else '#ef5350'
            st.markdown(f'''
            <div class="valuation-method">
                <div class="method-title">💼 EV/EBITDA Method</div>
                <div class="method-row">
                    <span class="method-label">Current EV/EBITDA</span>
                    <span class="method-value">{vals['current_ev_ebitda']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Industry EV/EBITDA</span>
                    <span class="method-value">{vals['industry_ev_ebitda']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">EBITDA</span>
                    <span class="method-value">${vals['ebitda']/1000000000:,.2f}B</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Fair Value (EV)</span>
                    <span class="method-value" style="color: {fair_color_ev}">${vals['fair_value_ev']:,.2f}</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Upside (EV)</span>
                    <span class="method-value" style="color: {upside_color_ev}">{vals['upside_ev']:+.2f}%</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("EV/EBITDA valuation not available")
    
    # Financial Data Table
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Complete Financial Summary</div>', unsafe_allow_html=True)
    
    financial_data = pd.DataFrame({
        'Metric': [
            'Current Price', 'Market Cap', 'Enterprise Value', 
            'PE Ratio (TTM)', 'Forward PE', 'EV/EBITDA',
            'P/B Ratio', 'P/S Ratio', 'EPS (TTM)',
            'EBITDA', 'Book Value', 'Net Debt',
            '52W High', '52W Low', 'Beta',
            'Dividend Yield', 'ROE', 'Profit Margin'
        ],
        'Value': [
            f"${vals['price']:,.2f}",
            f"${vals['market_cap']/1000000000:,.2f}B",
            f"${vals['enterprise_value']/1000000000:,.2f}B" if vals['enterprise_value'] else 'N/A',
            f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',
            f"{vals['forward_pe']:.2f}x" if vals['forward_pe'] else 'N/A',
            f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A',
            f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else 'N/A',
            f"{vals['ps_ratio']:.2f}x" if vals['ps_ratio'] else 'N/A',
            f"${vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A',
            f"${vals['ebitda']/1000000000:,.2f}B" if vals['ebitda'] else 'N/A',
            f"${vals['book_value']:.2f}" if vals['book_value'] else 'N/A',
            f"${vals['net_debt']/1000000000:,.2f}B",
            f"${vals['52w_high']:,.2f}" if vals['52w_high'] else 'N/A',
            f"${vals['52w_low']:,.2f}" if vals['52w_low'] else 'N/A',
            f"{vals['beta']:.2f}" if vals['beta'] else 'N/A',
            f"{vals['dividend_yield']*100:.2f}%" if vals['dividend_yield'] else 'N/A',
            f"{vals['roe']*100:.2f}%" if vals['roe'] else 'N/A',
            f"{vals['profit_margin']*100:.2f}%" if vals['profit_margin'] else 'N/A'
        ]
    })
    
    st.dataframe(
        financial_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("📊 Metric", width="medium"),
            "Value": st.column_config.TextColumn("📈 Value", width="medium")
        }
    )

else:
    # Welcome screen
    st.markdown('''
    <div class="info-box">
        <h3>👋 Welcome to US Stock Valuation Pro</h3>
        <p>Select a stock from the sidebar and click <strong>ANALYZE STOCK</strong> to get started.</p>
        <br>
        <strong>Features:</strong>
        <ul>
            <li>📊 Multi-factor valuation (PE, EV/EBITDA, P/B, DCF)</li>
            <li>📈 Professional charts and visualizations</li>
            <li>📥 Downloadable PDF reports</li>
            <li>🎯 Buy/Sell recommendations</li>
            <li>📋 Complete financial metrics</li>
            <li>🇺🇸 1,200+ NYSE & NASDAQ stocks</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

# Footer
st.markdown('''
<div class="footer">
    <p><strong>🇺🇸 US Stock Valuation Pro</strong> | Professional US Market Analysis Platform</p>
    <p style="font-size: 0.8rem; color: #64b5f6;">
        ⚠️ Disclaimer: This tool is for educational purposes only. 
        Always consult a qualified financial advisor before making investment decisions.
    </p>
</div>
''', unsafe_allow_html=True)
