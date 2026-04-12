import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import os
from PIL import Image
import time

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="LSS3 OTA Manager",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------- Compact CSS -------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 700px !important;
    }
    header { display: none; }
    .main-card {
        background: white;
        border-radius: 20px;
        padding: 1rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    h1 {
        font-size: 1.8rem !important;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .subhead {
        text-align: center;
        color: #4b5563;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .version-badge {
        background: #e6f0ff;
        color: #1e40af;
        border-radius: 40px;
        padding: 0.2rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .url-link {
        font-family: monospace;
        font-size: 0.8rem;
        background: #f1f5f9;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        word-break: break-all;
        display: inline-block;
        max-width: 100%;
        text-decoration: none;
        color: #2563eb;
    }
    .url-link:hover {
        text-decoration: underline;
    }
    .stButton button {
        background: linear-gradient(95deg, #2563eb, #1e40af);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.4rem 1.5rem;
        width: 100%;
    }
    .footer {
        text-align: center;
        margin-top: 1rem;
        padding-top: 0.5rem;
        font-size: 0.8rem;
        color: #6c757d;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
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

# ------------------- Firebase -------------------
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
            st.error(f"Firebase error: {e}")
            st.stop()
    else:
        if os.path.exists("ota.json"):
            cred = credentials.Certificate("ota.json")
        else:
            st.error("Missing Firebase credentials.")
            st.stop()
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fota-svm-default-rtdb.firebaseio.com/'
    })

init_firebase()
ref = db.reference('/OTA')

# ------------------- Header -------------------
st.markdown("<h1>LSS3 OTA Manager</h1>", unsafe_allow_html=True)
st.markdown('<div class="subhead">Manage over‑the‑air updates for your LSS3 devices</div>', unsafe_allow_html=True)

# ------------------- Load current data -------------------
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

# ------------------- Current Firmware Card -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("**📟 Currently deployed firmware**")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown(f"<span class='version-badge'>Version {current_version}</span>", unsafe_allow_html=True)
with col2:
    # Add "URL:" label and icon
    st.markdown("**URL:** 🔗", unsafe_allow_html=True)
    if current_url != "none" and current_url.startswith("http"):
        st.markdown(f"<a href='{current_url}' target='_blank' class='url-link'>{current_url}</a>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='url-link'>{current_url}</span>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Publish Card -------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("**✏️ Publish new firmware**")

new_version = st.text_input("Version", placeholder="e.g., 1.2.3", label_visibility="collapsed", key="ver")
new_url = st.text_input("Firmware URL", placeholder="https://...", label_visibility="collapsed", key="url")

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
        st.balloons()
        time.sleep(1)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Footer with bigger logo (width=100) -------------------
st.markdown('<div class="footer">', unsafe_allow_html=True)
if logo_img:
    st.image(logo_img, width=100, output_format="PNG")
st.markdown("**DeZignArena** — You Dream, We Design")
st.markdown('</div>', unsafe_allow_html=True)