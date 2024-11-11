import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array  # 用于加载图像

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')  # dataset folder with 'Absent' and 'Present' subfolders
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)  # Create 'models' directory if it doesn't exist

# Set the number of training epochs
epochs = 20  # Adjust as needed

# Function to load image files as data
def load_image_files(directory, target_size=(128, 128)):
    data = []
    labels = []
    for label, sub_dir in enumerate(['Absent', 'Present']):  # 'Absent' is label 0, 'Present' is label 1
        sub_dir_path = os.path.join(directory, sub_dir)
        print(f"Checking directory: {sub_dir_path}")  # Debug: Print directory path
        if not os.path.exists(sub_dir_path):
            print(f"Error: Directory {sub_dir_path} does not exist.")
            continue
        for file_name in os.listdir(sub_dir_path):
            print(f"Found file: {file_name}")  # Debug: Print each file name
            if file_name.endswith('.png'):  # Check for .png files
                file_path = os.path.join(sub_dir_path, file_name)
                print(f"Loading file: {file_path}")  # Debug: Print each file path
                try:
                    # Load image and convert to array
                    img = load_img(file_path, target_size=target_size, color_mode="grayscale")
                    img_array = img_to_array(img)
                    data.append(img_array)  # Append image array
                    labels.append(label)  # Append corresponding label (0 for Absent, 1 for Present)
                except Exception as e:
                    print(f"Error loading file {file_path}: {e}")
    
    # Convert lists to numpy arrays
    data = np.array(data)
    labels = np.array(labels)
    
    print(f"Final data shape: {data.shape}, Labels shape: {labels.shape}")  # Debug: print the shape of data to verify
    
    return data, labels

# Load dataset
X_train, y_train = load_image_files(DATASET_DIR)

# Check if data was loaded correctly
if X_train.shape[0] == 0:
    print("Error: No data was loaded. Please check the dataset directory and file format.")
    exit()

# Normalize data
X_train = X_train / 255.0  # Scale pixel values to [0, 1]

# Define the model architecture
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),  # First convolutional layer
    MaxPooling2D((2, 2)),  # Max pooling layer
    Conv2D(64, (3, 3), activation='relu'),  # Second convolutional layer
    MaxPooling2D((2, 2)),  # Max pooling layer
    Flatten(),  # Flatten layer to convert 2D data to 1D
    Dense(64, activation='relu'),  # Fully connected layer
    Dropout(0.5),  # Dropout layer for regularization
    Dense(1, activation='sigmoid')  # Output layer for binary classification
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=epochs, batch_size=32)

# Save the trained model
model.save(os.path.join(MODEL_DIR, 'heart_model.h5'))

# Print final training accuracy for debugging
print(f"Final training accuracy: {history.history['accuracy'][-1]}")
