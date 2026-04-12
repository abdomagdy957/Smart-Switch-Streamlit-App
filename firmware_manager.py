import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import os
from PIL import Image

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="LSS3 OTA Manager",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------- Custom CSS for Modern UI -------------------
st.markdown("""
<style>
    /* Main background and fonts */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9edf2 100%);
    }
    
    /* Card style for main content */
    .main-card {
        background: white;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Headers */
    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(120deg, #1e2a3a, #0f172a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    
    /* Subheader */
    .subhead {
        font-size: 1rem;
        color: #4b5563;
        margin-bottom: 2rem;
        border-left: 4px solid #3b82f6;
        padding-left: 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    /* Button */
    .stButton button {
        background: linear-gradient(95deg, #2563eb, #1e40af);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37,99,235,0.3);
        background: linear-gradient(95deg, #1e40af, #1e3a8a);
    }
    
    /* Input fields */
    .stTextInput input {
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    .stTextInput input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        font-size: 0.8rem;
        color: #6c757d;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .company-logo {
        max-height: 80px;
        margin-bottom: 1rem;
    }
    
    /* Version badge */
    .version-badge {
        background: #e6f0ff;
        color: #1e40af;
        border-radius: 40px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Success message */
    .stSuccess {
        background: #dcfce7;
        border-left: 5px solid #22c55e;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- Load Logo -------------------
def load_logo():
    # Try to load local logo file
    if os.path.exists("logo.png"):
        return Image.open("logo.png")
    elif os.path.exists("logo.jpg"):
        return Image.open("logo.jpg")
    else:
        # Fallback: use a custom text logo if file missing
        return None

logo_img = load_logo()

# ------------------- Firebase Initialization -------------------
def init_firebase():
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    if 'FIREBASE_CRED' in st.secrets:
        try:
            cred_dict = json.loads(st.secrets["FIREBASE_CRED"])
            cred = credentials.Certificate(cred_dict)
        except Exception as e:
            st.error(f"Invalid FIREBASE_CRED secret: {e}")
            st.stop()
    else:
        if os.path.exists("ota.json"):
            cred = credentials.Certificate("ota.json")
        else:
            st.error("Firebase credentials not found.")
            st.stop()

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fota-svm-default-rtdb.firebaseio.com/'
    })

init_firebase()
ref = db.reference('/OTA')

# ------------------- UI Header with Logo -------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if logo_img:
        st.image(logo_img, use_container_width=True, output_format="PNG")
    else:
        st.markdown('<div class="logo-container"><span style="font-size:2rem;">⚡</span></div>', unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center;">LSS3 OTA Manager</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4b5563;">Firmware updates made simple</p>', unsafe_allow_html=True)
st.markdown('<div class="subhead">📡 Manage over‑the‑air updates for your LSS3 devices</div>', unsafe_allow_html=True)

# ------------------- Load Current Firmware Info -------------------
current_data = ref.get()
if current_data and isinstance(current_data, dict):
    if 'app' in current_data:
        current_version = current_data['app'].get('version', 'none')
        current_url = current_data['app'].get('url', 'none')
    else:
        current_version = current_data.get('version', 'none')
        current_url = current_data.get('url', 'none')
else:
    current_version = "none"
    current_url = "none"

# ------------------- Current Status Card -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("### 📟 Currently deployed firmware")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"**Version**  <span class='version-badge'>{current_version}</span>", unsafe_allow_html=True)
with col_b:
    st.markdown(f"**URL**  `{current_url}`", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Publish New Firmware Card -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("### ✏️ Publish new firmware")

new_version = st.text_input("Firmware version", placeholder="e.g., 1.2.3", key="version_input")
new_url = st.text_input("Firmware binary URL", placeholder="https://example.com/firmware.bin", key="url_input")

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🚀 Publish update", use_container_width=True):
        if not new_version or not new_url:
            st.error("Both version and URL are required.", icon="⚠️")
        else:
            data_to_write = {
                "app": {
                    "version": new_version,
                    "url": new_url
                }
            }
            ref.set(data_to_write)
            st.success(f"✅ Version **{new_version}** published successfully!")
            st.balloons()
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Footer with Company Logo -------------------
st.markdown('<div class="footer">', unsafe_allow_html=True)
if logo_img:
    st.image(logo_img, width=100, output_format="PNG")
st.markdown("**DeZignArena** — You Dream, We Design")
st.markdown("Devices check for updates every 5 minutes or on reboot.")
st.markdown('</div>', unsafe_allow_html=True)