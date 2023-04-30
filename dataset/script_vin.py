from os import makedirs, remove, walk, path
from pathlib import Path
from shutil import copyfile
import hashlib

DEST_DIR = "modif"
EXTENSION_TO_COPY = ".wav"

def file_shasum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[0:6]

filepaths = []
curr_path = path.dirname(__file__)
for (dirpath, _, filenames) in walk(curr_path):
    if DEST_DIR in dirpath: continue
    filepaths.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(EXTENSION_TO_COPY))
for i, filepath in enumerate(filepaths):
    copyfile(filepath, file_shasum(filepath))
    

