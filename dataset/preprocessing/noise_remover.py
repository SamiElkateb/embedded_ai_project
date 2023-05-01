import librosa
from os import path, walk, remove, makedirs, listdir
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
    for folder_name in listdir(data_path):
        folder_path = path.join(data_path, folder_name)
        try:
            for file_name in listdir(folder_path):
                file_path = path.join(folder_path, file_name)
                features = extract_features(file_path)
                X.append(features)
                labels.append(folder_name)
                filepaths.append(file_path)
        except NotADirectoryError:
            print("not a dir")
            continue
    y = label_encoder.fit_transform(labels)
    return np.array(X), np.array(y), filepaths

def remove_files(data_path):
    misclasified_list = []
    with open(data_path, 'r') as misclasified_file:
        for line in misclasified_file:
            misclasified_list.append(line.strip())
    for _, filepath in enumerate(misclasified_list):
        absolute_path = path.dirname(__file__)
        full_path = path.join(absolute_path, "../" + filepath.replace('./dataset/', ''))
        print(full_path)
        # break
        remove(full_path)


def remove_noise(data_path):
    # X, y, filepaths = load_data(data_path)
    # print("X", X)
    # print("y", y)
    # flag_potentially_noisy_data(X, y, filepaths, thres=.5, output_file=f"{data_path}/misclassified_data.txt")
    remove_files(f"{data_path}/misclassified_data.txt")

