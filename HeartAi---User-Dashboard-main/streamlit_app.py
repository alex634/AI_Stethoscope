import streamlit as st
import requests
import hashlib
import datetime

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8080"

# Helper function to hash passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Navigation and Main Logic
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        main_app()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()

# Login Page
def login_page():
    st.title("Login")
    role = st.radio("Select your role", ["Doctor", "Patient"], key="login_role")  # Add role selection
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        hashed_password = hash_password(password)
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"username": username, "password_md5": hashed_password}
        )

        if response.status_code == 200:
            data = response.json()
            if data["role"] == role.lower():  # Check if role matches
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.password_md5 = hashed_password
                st.session_state.role = role  # Save role in session state
                st.success("Login successful!")
            else:
                st.error("Role mismatch. Please check your selected role.")
        else:
            st.error("Invalid username or password.")

    if st.button("Go to Register"):
        st.session_state.page = "register"

# Registration Page
def register_page():
    st.title("Register")
    role = st.radio("Select your role", ["Doctor", "Patient"], key="register_role")  # Add role selection
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        hashed_password = hash_password(password)
        response = requests.post(
            f"{BACKEND_URL}/createuser",
            json={"username": username, "password_md5": hashed_password, "role": role.lower()}
        )

        if response.status_code == 200:
            st.success("Registration successful! Please log in.")
            st.session_state.page = "login"
        elif response.status_code == 400:
            st.error("Username already exists.")
        else:
            st.error("Failed to register. Please try again.")

    if st.button("Back to Login"):
        st.session_state.page = "login"

# Main Application (After Login)
def main_app():
    st.title(f"Welcome, {st.session_state['username']} ({st.session_state['role']})!")

    tab1, tab2 = st.tabs(["Upload and Analyze", "View History"])

    # Upload Tab
    with tab1:
        st.subheader("Upload and Analyze")
        patient_name = st.text_input("Patient Name")
        uploaded_file = st.file_uploader("Upload heartbeat audio file (WAV/FLAC)", type=["wav", "flac"])

        if st.button("Analyze"):
            if uploaded_file and patient_name:
                files = {"file": (uploaded_file.name, uploaded_file.read())}
                data = {
                    "username": st.session_state.username,
                    "password_md5": st.session_state.password_md5,
                    "patient_name": patient_name
                }
                response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis complete!")
                    st.write("Inference Result:", result["inference"])
                else:
                    st.error("Failed to process file.")
            else:
                st.error("Please provide patient name and file.")

    # History Tab
    with tab2:
        st.subheader("View History")
        response = requests.get(
            f"{BACKEND_URL}/accesshistory",
            params={"username": st.session_state.username, "password_md5": st.session_state.password_md5}
        )

        if response.status_code == 200:
            history = response.json()
            for record in history:
                with st.expander(f"{record['patient_name']} - {datetime.datetime.fromtimestamp(record['epoch'])}"):
                    if st.button(f"View Details for ID {record['id']}", key=f"view_{record['id']}"):
                        details = requests.get(f"{BACKEND_URL}/history/{record['id']}")
                        if details.status_code == 200:
                            details_data = details.json()
                            st.write("Patient Name:", details_data["patient_name"])
                            st.write("Inference:", details_data["inference"])
                            st.write("File Path:", details_data["file_path"])
                        else:
                            st.error("Failed to load details.")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

# Run the application
if __name__ == "__main__":
    main()
