import os
import shutil
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')
TRAIN_DIR = os.path.join(BASE_DIR, '..', 'train')
TEST_DIR = os.path.join(BASE_DIR, '..', 'test')
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

def separate_dataset(test_ratio=0.2):
    files = [f for f in os.listdir(DATASET_DIR) if f.endswith('.wav')]
    random.shuffle(files)
    split_point = int(len(files) * (1 - test_ratio))
    train_files = files[:split_point]
    test_files = files[split_point:]
    
    for file in train_files:
        shutil.copy(os.path.join(DATASET_DIR, file), TRAIN_DIR)
    for file in test_files:
        shutil.copy(os.path.join(DATASET_DIR, file), TEST_DIR)

separate_dataset()
