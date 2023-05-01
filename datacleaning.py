import librosa
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Define the function to extract features from audio files
def extract_features(audio_path):
    y, sr = librosa.load(audio_path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfccs.T, axis=0)

def detect_noisy_samples(X, y, thres=.5, output_file=None):
    rf = RandomForestClassifier(oob_score=True).fit(X, y)
    print(range(len(y)))
    noise_prob = 1 - rf.oob_decision_function_[range(len(y)), y.astype(int)]
    noisy_indexes = noise_prob > thres
    if output_file is not None:
        with open(output_file, 'w') as f:
            for i in noisy_indexes:
                f.write(f'{X[i]}\n')  # Write file path to output file
    return noisy_indexes

# Define the function to load audio files and extract features
def load_data(data_path):
    X = []
    labels = []
    paths = []
    label_encoder = LabelEncoder()
    i = 0
    for folder_name in os.listdir(data_path):
        folder_path = os.path.join(data_path, folder_name)
        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                features = extract_features(file_path)
                X.append(features)
                labels.append(folder_name)
                paths.append(file_path)
                i+= 1
                if i > 10: break

        except NotADirectoryError:
            continue
    y = label_encoder.fit_transform(labels)
    return np.array(X), np.array(y), labels, paths
# Load the audio data
data_path = './dataset/dataset_v2/'
X, y, labels, file_paths = load_data(data_path)
print("data loaded")
print("X", X)
print("Y", y)
print("labels", labels)

# Detect mislabeled audio data
noisy_indexes = detect_noisy_samples(X, y, thres=.5, output_file='./dataset/dataset_v2/misclassified_data.txt')

# Print the indices of the mislabeled audio data
print("Mislabeled audio data:", np.where(noisy_indexes)[0])
