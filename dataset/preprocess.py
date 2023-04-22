from pathlib import Path
from os import walk, path
from preprocessing import DEST_DIR, NOSILENCE_DIR, RESAMPLED_DIR, convert, remove_silence, ceil_by_min_size, add_tmp_dir

if __name__ == '__main__':
    filepaths = []
    curr_path = path.dirname(__file__)
    for (dirpath, dirnames, filenames) in walk(curr_path):
        if DEST_DIR in dirpath: continue
        if NOSILENCE_DIR in dirpath: continue
        if RESAMPLED_DIR in dirpath: continue
        filepaths.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".wav"))
    filepaths = ceil_by_min_size(filepaths)
    for filepath in filepaths:
        resampled_path = add_tmp_dir(filepath, RESAMPLED_DIR)
        nosilence_path = add_tmp_dir(filepath, NOSILENCE_DIR)
        convert(filepath, resampled_path)
        remove_silence(resampled_path, nosilence_path, 3)
        break
