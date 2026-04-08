import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import os

# ---------- Firebase initialization ----------
# For Streamlit Cloud, store the JSON content as a secret.
# For local testing, load from file.

def init_firebase():
    try:
        # Try to get Firebase app if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized yet
        if 'FIREBASE_CRED' in st.secrets:
            # Running on Streamlit Cloud – load from secrets
            cred_dict = json.loads(st.secrets["FIREBASE_CRED"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Local development – use the downloaded JSON file
            # Make sure the file is in the same folder
            cred = credentials.Certificate("ota.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fota-svm-default-rtdb.firebaseio.com/'
        })

init_firebase()

# Reference to OTA node
ref = db.reference('/OTA')

st.set_page_config(page_title="FOTA Manager", page_icon="📲")
st.title("📲 ESP32 OTA Firmware Manager")
st.markdown("Set the firmware version and download URL for your devices.")

# Load current values
current_data = ref.get()
if current_data and isinstance(current_data, dict):
    # Try both JSON formats
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
        # Write in the "app" object format (preferred by your device)
        data_to_write = {
            "app": {
                "version": new_version,
                "url": new_url
            }
        }
        # Optionally also keep a legacy root-level copy for compatibility
        # ref.update(data_to_write) would merge; we want to set the whole node.
        ref.set(data_to_write)
        st.success(f"Published version **{new_version}** to Firebase!")
        st.balloons()

st.markdown("---")
st.caption("Devices will check for updates every 5 minutes or on reboot.")