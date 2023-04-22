from mutagen.wave import WAVE
from mutagen.mp3 import MP3
from pydub import AudioSegment
from shutil import copyfile, rmtree
from os import walk, path, makedirs, stat, remove
from random import shuffle, choice
import numpy as np
import hashlib
import tarfile
import math
from pathlib import Path

DEST_DIR="dataset.v2"
TMP_DIR="dataset.tmp.v2"

def convert_mp3_wav(src: str):
    dst = src.replace(".mp3", ".wav")
    if path.exists(dst): return
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")

def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[0:6]

def get_sound_lengths(sound_files: list[str]) -> np.ndarray:
    SOUND_LIB = MP3 if sound_files[0].endswith("mp3") else WAVE
    arr = np.empty(len(sound_files))
    for i, sound_file in enumerate(sound_files):
        try:
            audio = SOUND_LIB(sound_file)
            arr[i] = int(audio.info.length)
        except:
            print(sound_file, type)
    return arr

def remove_outliers(sound_files: list[str], first_quartile, third_quartile):
    SOUND_LIB = MP3 if sound_files[0].endswith("mp3") else WAVE
    result_array = []
    for sound_file in sound_files:
        try:
            audio = SOUND_LIB(sound_file)
            audio_length = int(audio.info.length)
            if audio_length > first_quartile and audio_length < third_quartile:
                result_array.append(sound_file)
        except:
            print(sound_file, type)
    return result_array

def get_min_total_size(sound_files_paths: list[str]):
    totals = {}
    classes = []
    for sound_file_path in sound_files_paths:
        filepath = Path(sound_file_path)
        classname = filepath.parent.name
        size = stat(sound_file_path).st_size / (1024 * 1024)
        if not classname in totals:
            totals[classname] = 0
            classes.append(classname)

        totals[classname] += size
    min = + math.inf
    for classname in classes:
        if totals[classname] < min:
            min = totals[classname]
    print("result", totals)
    print("min", min)
    return min



def clamp_data_size(sound_files_paths: list[str], max_size: int):
    totals = {}
    classes = []
    res = []
    for sound_file_path in sound_files_paths:
        filepath = Path(sound_file_path)
        classname = filepath.parent.name
        size = stat(sound_file_path).st_size / (1024 * 1024)
        if not classname in totals:
            totals[classname] = 0
            classes.append(classname)

        if totals[classname] + size < max_size + 1:
            res.append(sound_file_path)
            totals[classname] += size
    return res

def populate_dest_data(sound_file_paths: list[str]):
    result_array = []
    for sound_file_path in sound_file_paths:
        _, extension = path.splitext(sound_file_path)
        filename = sha256sum(sound_file_path) + extension
        filepath = Path(sound_file_path)
        dirname = filepath.parent.name
        result_array.append({
            "curr_path": sound_file_path,
            "dest_filename": filename,
            "dest_dirname": dirname,
        })
    return result_array

def make_archive(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname='.')

def copy_files(sound_file_datas):
    for sound_file_data in sound_file_datas:
        src_path = sound_file_data["curr_path"]
        absolute_path = path.dirname(__file__)
        relative_path = f"{DEST_DIR}/{sound_file_data['dest_dirname']}/{sound_file_data['dest_filename']}"
        dest_path = path.join(absolute_path, relative_path)
        makedirs(path.dirname(dest_path), exist_ok=True)
        copyfile(src_path, dest_path)

def create_testing_list(sound_file_datas):
    relative_path = f"{DEST_DIR}/testing_list.txt"
    absolute_path = path.dirname(__file__)
    testing_file_path = path.join(absolute_path, relative_path)
    makedirs(path.dirname(testing_file_path), exist_ok=True)
    if path.exists(testing_file_path):
        remove(testing_file_path)
    with open(testing_file_path,"a+") as file:
        for sound_file_data in sound_file_datas:
            dest_dir=sound_file_data["dest_dirname"]
            dest_filename=sound_file_data["dest_filename"]
            file.write(f'{dest_dir}/{dest_filename}\n')

def reset_testing_list():
    relative_path = f"{DEST_DIR}/testing_list.txt"
    absolute_path = path.dirname(__file__)
    testing_file_path = path.join(absolute_path, relative_path)
    makedirs(path.dirname(testing_file_path), exist_ok=True)
    if path.exists(testing_file_path):
        remove(testing_file_path)

def split_sound(sound_data):
    curr_path = sound_data["curr_path"]
    absolute_path = path.dirname(__file__)
    dest_dirname = sound_data['dest_dirname']
    dest_filename, extension = path.splitext(sound_data['dest_filename'])
    audio_length = int(WAVE(curr_path).info.length)
    audio = AudioSegment.from_wav(curr_path)

    relative_path = f"{DEST_DIR}/testing_list.txt"
    absolute_path = path.dirname(__file__)
    testing_file_path = path.join(absolute_path, relative_path)

    with open(testing_file_path,"a+") as file:
        for i in range(audio_length):
            t1 = i * 1000
            t2 = t1 + 1000
            cut_audio = audio[t1:t2]
            relative_path = f"{DEST_DIR}/{dest_dirname}/{dest_filename}_{i}{extension}"
            dest_path = path.join(absolute_path, relative_path)
            makedirs(path.dirname(dest_path), exist_ok=True)
            cut_audio.export(dest_path, format="wav")
            if choice([True, False, False]):
                file.write(f'{dest_dirname}/{dest_filename}_{i}{extension}\n')


if __name__ == '__main__':

    curr_path = path.dirname(__file__)
    filepaths_mp3 = []
    for (dirpath, dirnames, filenames) in walk(curr_path):
        if DEST_DIR in dirpath: continue
        if TMP_DIR in dirpath: continue
        filepaths_mp3.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".mp3"))

    for filepath in filepaths_mp3:
        convert_mp3_wav(filepath)
    print("converted mp3 to wav")

    filepaths_wav = []
    for (dirpath, dirnames, filenames) in walk(curr_path):
        if DEST_DIR in dirpath: continue
        if TMP_DIR in dirpath: continue
        filepaths_wav.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".wav"))

    shuffle(filepaths_wav)
    sound_lengths = get_sound_lengths(filepaths_wav)
    first_quartile = np.quantile(sound_lengths, .25)
    third_quartile = np.quantile(sound_lengths, .75)

    print("calculated stats on sounds")

    sanitized_sounds = remove_outliers(filepaths_wav, first_quartile, third_quartile)
    print("sanitized sounds")
    min_total_size = int(get_min_total_size(sanitized_sounds))
    shuffle(sanitized_sounds)
    clamped_data = clamp_data_size(sanitized_sounds, min_total_size)
    
    print("clamped sounds", len(clamped_data))

    populated_sounds = populate_dest_data(clamped_data)
    print("populated sounds")

    relative_path = f"{DEST_DIR}/"
    absolute_path = path.dirname(__file__)
    destdirpath = path.join(absolute_path, relative_path)
    if path.exists(destdirpath):
        rmtree(destdirpath)

    reset_testing_list()
    # create_testing_list(populated_sounds)
    # print("created testing list")

    for populated_sound in populated_sounds:
        split_sound(populated_sound) 
    # copy_files(populated_sounds)
    print("split files")

    make_archive(f"{DEST_DIR}.tar.gz", DEST_DIR)
    print("made archive")
