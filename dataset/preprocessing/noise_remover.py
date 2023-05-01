import librosa
from os import path, walk, remove, makedirs
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def extract_features(audio_path):
    y, sr = librosa.load(audio_path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfccs.T, axis=0)

def flag_potentially_noisy_data(X, y, file_paths, thres=.5, output_file=None):
    rf = RandomForestClassifier(oob_score=True).fit(X, y)
    noise_prob = 1 - rf.oob_decision_function_[range(len(y)), y]
    noisy_indexes = noise_prob > thres
    if output_file is not None:
        with open(output_file, 'w') as f:
            for i, is_noisy in enumerate(noisy_indexes):
                if is_noisy:
                    f.write(f'{file_paths[i]}\n')
    return noisy_indexes

def load_data(data_path):
    X = []
    labels = []
    filepaths = []
    label_encoder = LabelEncoder()
    i = 0
    for (dirpath, dirnames, filenames) in walk(data_path):
        filepaths.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".wav"))
        labels.extend(dirnames)
        i += 1
        print("for")
        if i == 2: break
    print(labels)
    for filepath in filepaths:
        features = extract_features(filepath)
        X.append(features)
        i += 4
        print("for")
        if i > 4: break
    y = label_encoder.fit_transform(labels)
    return np.array(X), np.array(y), filepaths

def remove_files(data_path):
    misclasified_list = []
    with open(data_path, 'r') as misclasified_file:
        for line in misclasified_file:
            misclasified_list.append(line.strip())
    for _, filepath in enumerate(misclasified_list):
        absolute_path = path.dirname(__file__)
        full_path = path.join(absolute_path, filepath.replace('./dataset/', ''))
        print(full_path)
        # remove(full_path)


def remove_noise(data_path):
    X, y, filepaths = load_data(data_path)
    print("X", X)
    print("y", y)
    flag_potentially_noisy_data(X, y, filepaths, thres=.5, output_file=f"{data_path}/misclassified_data.txt")
    remove_files(f"{data_path}/misclassified_data.txt")

