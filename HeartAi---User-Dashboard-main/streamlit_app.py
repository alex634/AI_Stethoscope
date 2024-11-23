import streamlit as st
import requests
import hashlib

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8080"

# Helper function to hash passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Login or Sign-Up Page
def login_signup_page():
    st.title("Welcome to the Heartbeat Analysis System")
    mode = st.radio("Login or Sign Up", ["Log In", "Sign Up"], key="mode")

    if mode == "Log In":
        st.subheader("Log In")
    else:
        st.subheader("Sign Up")

    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Log In" if mode == "Log In" else "Sign Up"):
        if username and password:
            hashed_password = hash_password(password)
            if mode == "Log In":
                # Call backend for login
                response = requests.post(
                    f"{BACKEND_URL}/login",
                    json={"username": username, "password_md5": hashed_password},
                )
                if response.status_code == 200:
                    st.session_state["username"] = username
                    st.session_state["password_md5"] = hashed_password
                    st.session_state["logged_in"] = True
                else:
                    st.error("Invalid credentials! Please try again.")
            else:
                # Call backend for sign-up
                response = requests.post(
                    f"{BACKEND_URL}/createuser",
                    json={"username": username, "password_md5": hashed_password},
                )
                if response.status_code == 200:
                    st.success("Sign-up successful! Please log in.")
                elif response.status_code == 400:
                    st.error("Username already exists. Please choose another.")
                else:
                    st.error("Failed to sign up. Please try again later.")
        else:
            st.warning("Please fill in all fields.")

# Main Page
def main_page():
    st.title(f"Welcome, {st.session_state['username']}!")
    if st.button("Log Out"):
        logout()

    # Tabs for Upload and History
    tabs = st.tabs(["Upload and Analyze", "Access History"])
    
    with tabs[0]:  # "Upload and Analyze" section
        st.header("Upload and Analyze Heartbeat Data")
        uploaded_file = st.file_uploader("Upload a heartbeat audio file (WAV/FLAC)", type=["wav", "flac"])
        if uploaded_file:
            response = requests.post(
                f"{BACKEND_URL}/upload",
                files={"file": uploaded_file},
                json={
                    "username": st.session_state["username"],
                    "password_md5": st.session_state["password_md5"],
                },
            )
            if response.status_code == 200:
                data = response.json()
                st.success("File uploaded and analyzed successfully!")
                st.write(f"Prediction: {data['prediction']}")
                st.image(data["spectrogram_image_url"])
            else:
                st.error("Failed to analyze the file. Please try again.")

    with tabs[1]:  # "Access History" section
        st.header("Access History")
        response = requests.get(
            f"{BACKEND_URL}/accesshistory",
            json={
                "username": st.session_state["username"],
                "password_md5": st.session_state["password_md5"],
            },
        )
        if response.status_code == 200:
            history = response.json()
            if history and "epochs" in history and len(history["epochs"]) > 0:
                st.write("Patient history (sorted by recent analysis):")
                for record in history["epochs"]:
                    st.write(record)
            else:
                st.info("No data record found.")
        else:
            st.error("Failed to load history. Please try again.")

# Logout function
def logout():
    st.session_state.clear()
    st.session_state["logged_in"] = False

# Streamlit Main
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_page()
else:
    login_signup_page()
