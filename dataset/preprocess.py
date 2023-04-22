from os import makedirs, remove, walk, path
import sys
import tarfile
from preprocessing import *
from shutil import rmtree
import logging
FORMAT = "%(message)s"
logging.basicConfig(level = logging.INFO, format=FORMAT)

def __make_archive(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname='.')

def __reset_file(filename: str):
    relative_path = f"{DEST_DIR}/${filename}"
    absolute_path = path.dirname(__file__)
    testing_file_path = path.join(absolute_path, relative_path)
    makedirs(path.dirname(testing_file_path), exist_ok=True)
    if path.exists(testing_file_path):
        remove(testing_file_path)

# resamples the dataset sound files and removes the silences
def clean():
    filepaths = []
    curr_path = path.dirname(__file__)
    for (dirpath, _, filenames) in walk(curr_path):
        if DEST_DIR in dirpath: continue
        if NOSILENCE_DIR in dirpath: continue
        if RESAMPLED_DIR in dirpath: continue
        filepaths.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".wav") or filename.endswith(".mp3"))
    nb_files = len(filepaths)
    logging.info(f"added {nb_files} sound files to be cleaned" )
    for i, filepath in enumerate(filepaths):
        resampled_path = add_tmp_dir(filepath, RESAMPLED_DIR).replace(".mp3", ".wav")
        nosilence_path = add_tmp_dir(filepath, NOSILENCE_DIR)
        convert(filepath, resampled_path)
        remove_silence(resampled_path, nosilence_path, 3)
        if i % int(nb_files/10) == 0:
            logging.info(f"cleaned {i}/{nb_files} files" )

# cuts the sounds in 1 second files
def cut():
    filepaths = []
    curr_path = path.dirname(__file__)
    for (dirpath, _, filenames) in walk(curr_path):
        if not NOSILENCE_DIR in dirpath: continue
        filepaths.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith(".wav"))
    nb_files = len(filepaths)
    logging.info(f"added {nb_files} sound total files" )
    filepaths = ceil_by_min_size(filepaths)
    logging.info(f"kept {nb_files} sound files" )
    populated_paths = populate_dest_data(filepaths)
    nb_files = len(populated_paths)
    logging.info(f"populated {nb_files} sound files" )

    relative_path = f"{DEST_DIR}/"
    absolute_path = path.dirname(__file__)
    absolute_dest_dir_path = path.join(absolute_path, relative_path)
    if path.exists(absolute_dest_dir_path):
        rmtree(absolute_dest_dir_path)

    __reset_file("testing_list.txt")
    __reset_file("datafile.txt")
    for i, populated_path in enumerate(populated_paths):
        split_sound(populated_path, absolute_dest_dir_path, "datafile.txt") 
        if i % int(nb_files/10) == 0:
            logging.info(f"cut {i}/{nb_files} files" )
    
# archives the destination folder
def archive():
    logging.info(f"creating archive from {DEST_DIR}")
    __make_archive(f"{DEST_DIR}.tar.gz", DEST_DIR)
    logging.info(f"creat archive from {DEST_DIR}.tar.gz")

def __main(arg):
    if arg == 'clean':
        clean()
    if arg == 'cut':
        cut()
    if arg == 'archive':
        archive()

if __name__ == '__main__':
    if len(sys.argv[1:]) != 1 and ("clean" in sys.argv[1] or "cut" in sys.argv[1] or "archive" in sys.argv[1]):
        sys.stderr.write(
            'Usage: preprocess.py <clean | cut | archive>\n')
        sys.exit(1)
    __main(sys.argv[1])
