import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import os

def init_firebase():
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    # Try to load credentials from Streamlit secrets
    if 'FIREBASE_CRED' in st.secrets:
        try:
            cred_dict = json.loads(st.secrets["FIREBASE_CRED"])
            cred = credentials.Certificate(cred_dict)
        except Exception as e:
            st.error(f"Invalid FIREBASE_CRED secret: {e}")
            st.stop()
    else:
        # For local development – you can keep a fallback file (optional)
        if os.path.exists("ota.json"):
            cred = credentials.Certificate("ota.json")
        else:
            st.error("Firebase credentials not found. Please set the 'FIREBASE_CRED' secret in Streamlit Cloud.")
            st.info("Go to Settings → Secrets and add a key named 'FIREBASE_CRED' with the content of your service account JSON.")
            st.stop()

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fota-svm-default-rtdb.firebaseio.com/'
    })

init_firebase()

# Rest of your app (unchanged)
ref = db.reference('/OTA')

st.set_page_config(page_title="FOTA Manager", page_icon="📲")
st.title("📲 ESP32 OTA Firmware Manager")
st.markdown("Set the firmware version and download URL for your devices.")

# Load current values
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

st.subheader("📡 Currently deployed firmware")
st.write(f"**Version:** `{current_version}`")
st.write(f"**URL:** `{current_url}`")

st.markdown("---")
st.subheader("✏️ Publish new firmware")

new_version = st.text_input("Firmware version (e.g. 1.2.3)", value="")
new_url = st.text_input("Firmware binary URL (https://...)", value="")

if st.button("🚀 Publish to Firebase"):
    if not new_version or not new_url:
        st.error("Both version and URL are required.")
    else:
        data_to_write = {
            "app": {
                "version": new_version,
                "url": new_url
            }
        }
        ref.set(data_to_write)
        st.success(f"Published version **{new_version}** to Firebase!")
        st.balloons()

st.markdown("---")
st.caption("Devices will check for updates every 5 minutes or on reboot.")