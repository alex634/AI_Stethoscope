# HeartAI - Heart Sound Analysis System

HeartAI is an integrated platform designed to upload, process, and analyze heart sound recordings using machine learning models. This tool is intended for healthcare professionals and users to identify potential heart conditions through spectrogram analysis.

## Features
- Upload and store heart sound recordings
- Convert recordings to spectrograms for analysis
- Train and test machine learning models on heart sound data
- User and doctor login functionality with respective dashboards
- View and analyze past recordings and their results

## Project Structure

/HeartAi 
	├── app.py # Backend server 
	├── app_frontend.py # Streamlit-based frontend 
	├── dataset # Directory for heart sound recordings (.wav) 
	├── helper_tools # Python scripts for dataset management and spectrogram generation │ 
		├── separate_dataset.py 
		│ └── spectrogram_generator.py 
	├── spectrograms # Spectrogram image storage 
	├── train # Training dataset folder 
	├── test # Test dataset folder 
	├── heart_model.h5 # Trained machine learning model 
	├── heart_data.db # SQLite database for user and recording data 
	├── README.md # Project documentation 
	└── setup.sh # Script for environment setup



## Prerequisites
- Python 3.8 or higher
- pip
- Virtual environment (recommended)

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone git@github.com:hmj2000/HeartAi---User-Dashboard.git
   cd HeartAi
   
2. Run the setup script to install dependencies:
   bash setup.sh
   python3 app.py
   streamlit run app_frontend.py

Usage
Upload heart sound recordings through the frontend.
View uploaded recordings and analysis results in the dashboard.
Train the machine learning model (if needed) using train_model.py.
Troubleshooting
Ensure all Python packages are up-to-date, and necessary Python modules are installed. If TensorFlow or other libraries encounter compatibility issues, refer to the library documentation for solutions.



