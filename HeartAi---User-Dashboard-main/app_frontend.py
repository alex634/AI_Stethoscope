import streamlit as st
import requests
from PIL import Image
import io
import os

# Set the URL for the Flask backend
backend_url = "https://516299ad-8520-43fc-8c68-ea6726ba6def-00-22s50ndij9nvh.spock.replit.dev"

# Set up the uploads folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("Heart Sound Analysis App")
st.header("Upload Your Heart Sound Recording for Analysis")

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Save the uploaded file locally
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write(f"File '{uploaded_file.name}' uploaded successfully.")

    # Send the file to the Flask backend
    if backend_url:
        with open(file_path, "rb") as file:
            response = requests.post(f"{backend_url}/upload", files={'file': file})

        # Check the backend's response
        if response.status_code == 200:
            try:
                # Parse JSON response from the backend
                data = response.json()
                st.write("Analysis Result:", data.get("prediction", "Unknown"))

                # Display the analyzed spectrogram image
                image_url = f"{backend_url}/download/{uploaded_file.name.replace('.wav', '_analyzed.png')}"
                image_response = requests.get(image_url)
                
                if image_response.status_code == 200:
                    # Display image in Streamlit
                    image = Image.open(io.BytesIO(image_response.content))
                    st.image(image, caption="Analyzed Spectrogram")
                else:
                    st.write("Error: Could not retrieve the analyzed spectrogram image.")
            except ValueError:
                st.write("Error: The server did not return JSON data.")
        else:
            st.write(f"Error: {response.status_code} - {response.text}")
    else:
        st.write("Error: BACKEND_URL is not set.")
