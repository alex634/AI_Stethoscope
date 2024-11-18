import streamlit as st
import requests
import hashlib

# Flask API Base URL
API_URL = "http://127.0.0.1:8080"  

# Helper function to hash passwords using MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Streamlit Application
st.title("Heartbeat Management System")

# Tabs for functionality
tab1, tab2, tab3 = st.tabs(["Create User", "Access History", "Upload and Analyze"])

# Tab 1: Create User
with tab1:
    st.header("Create a New User")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create User"):
        if username and password:
            password_md5 = hash_password(password)
            data = {"username": username, "password_md5": password_md5}
            try:
                response = requests.post(f"{API_URL}/createuser", json=data)
                if response.status_code == 200:
                    st.success("User created successfully!")
                elif response.status_code == 400:
                    st.error("Username already exists.")
                else:
                    st.error(f"Error: {response.json().get('error_string', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {e}")
        else:
            st.error("Please provide a username and password.")

# Tab 2: Access History
with tab2:
    st.header("Access User History")
    username = st.text_input("Username (History)", key="history_username")
    password = st.text_input("Password (History)", type="password", key="history_password")
    record_count = st.number_input("Number of Records", min_value=1, max_value=50, value=10, step=1)

    if st.button("View History"):
        if username and password:
            password_md5 = hash_password(password)
            data = {
                "username": username,
                "password_md5": password_md5,
                "record_count": record_count
            }
            try:
                response = requests.get(f"{API_URL}/accesshistory", json=data)
                if response.status_code == 200:
                    history = response.json()
                    st.write(f"Folder: {history['folder']}")
                    st.write("Epochs:", history['epochs'])
                elif response.status_code == 401:
                    st.error("Invalid username or password.")
                else:
                    st.error("Failed to fetch history.")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {e}")
        else:
            st.error("Please provide username and password.")

# Tab 3: Upload and Analyze
with tab3:
    st.header("Upload and Analyze Heartbeat Data")
    username = st.text_input("Username (Upload)", key="upload_username")
    password = st.text_input("Password (Upload)", type="password", key="upload_password")
    uploaded_file = st.file_uploader("Upload a WAV File", type=["wav"])

    if st.button("Upload and Analyze"):
        if username and password and uploaded_file:
            password_md5 = hash_password(password)
            files = {"file": uploaded_file}
            data = {"username": username, "password_md5": password_md5}
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    data=data,
                    files=files
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Prediction: {result['prediction']}")
                    spectrogram_url = f"{API_URL}{result['spectrogram_image_url']}"
                    st.image(spectrogram_url, caption="Generated Spectrogram")
                elif response.status_code == 401:
                    st.error("Invalid username or password.")
                else:
                    st.error(f"Error: {response.json().get('details', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {e}")
        else:
            st.error("Please provide username, password, and upload a file.")
