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

# ------------------- Compact CSS (No extra whitespace) -------------------
st.markdown("""
<style>
    /* Remove default padding/margins */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 700px !important;
    }
    /* Hide default streamlit top blank space */
    header {
        display: none;
    }
    /* Main card style */
    .main-card {
        background: white;
        border-radius: 20px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    /* Headings */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 0.25rem !important;
        text-align: center;
    }
    .subhead {
        text-align: center;
        color: #4b5563;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    /* Version badge */
    .version-badge {
        background: #e6f0ff;
        color: #1e40af;
        border-radius: 40px;
        padding: 0.2rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    /* URL line – wrap long URLs */
    .url-text {
        font-family: monospace;
        font-size: 0.8rem;
        background: #f1f5f9;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        word-break: break-all;
        white-space: normal;
        display: inline-block;
        max-width: 100%;
    }
    /* Button */
    .stButton button {
        background: linear-gradient(95deg, #2563eb, #1e40af);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.4rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    /* Footer minimal */
    .footer {
        text-align: center;
        margin-top: 1rem;
        padding-top: 0.5rem;
        font-size: 0.7rem;
        color: #9ca3af;
    }
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    .stTextInput > div {
        margin-bottom: 0.5rem;
    }
    hr {
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- Load Logo -------------------
def load_logo():
    if os.path.exists("logo.png"):
        return Image.open("logo.png")
    elif os.path.exists("logo.jpg"):
        return Image.open("logo.jpg")
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
            st.error(f"Firebase cred error: {e}")
            st.stop()
    else:
        if os.path.exists("ota.json"):
            cred = credentials.Certificate("ota.json")
        else:
            st.error("Firebase credentials missing.")
            st.stop()

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fota-svm-default-rtdb.firebaseio.com/'
    })

init_firebase()
ref = db.reference('/OTA')

# ------------------- Header with Logo (compact) -------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if logo_img:
        st.image(logo_img, use_container_width=True, output_format="PNG")
    else:
        st.markdown("### ⚡ LSS3")

st.markdown("<h1>LSS3 OTA Manager</h1>", unsafe_allow_html=True)
st.markdown('<div class="subhead">Manage over‑the‑air updates for your LSS3 devices</div>', unsafe_allow_html=True)

# ------------------- Load Current Firmware -------------------
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

# ------------------- Current Firmware Card (compact) -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("**📟 Currently deployed firmware**")
col_ver, col_url = st.columns([1, 2])
with col_ver:
    st.markdown(f"<span class='version-badge'>Version {current_version}</span>", unsafe_allow_html=True)
with col_url:
    # URL shown inline, wrapped
    st.markdown(f"<span class='url-text'>📎 {current_url}</span>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Publish New Firmware Card (compact) -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("**✏️ Publish new firmware**")

new_version = st.text_input("Version", placeholder="e.g., 1.2.3", key="ver", label_visibility="collapsed")
new_url = st.text_input("Firmware URL", placeholder="https://...", key="url", label_visibility="collapsed")

# Publish button
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
        st.success(f"✅ Version **{new_version}** published!")
        st.balloons()  # balloons go up
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Minimal Footer (no device check message) -------------------
st.markdown('<div class="footer">DeZignArena — You Dream, We Design</div>', unsafe_allow_html=True)