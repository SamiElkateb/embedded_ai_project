from os import makedirs, remove, walk, path
import sys
import tarfile
from preprocessing import *
from shutil import rmtree
import logging
from sklearn.model_selection import train_test_split
FORMAT = "%(message)s"
logging.basicConfig(level = logging.INFO, format=FORMAT)

def __make_archive(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname='.')

def __reset_file(filename: str):
    relative_path = f"{DEST_DIR}/{filename}"
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
        nosilence_path = add_tmp_dir(filepath, NOSILENCE_DIR).replace(".mp3", ".wav")
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
    # filepaths = ceil_by_min_size(filepaths)
    # logging.info(f"kept {nb_files} sound files" )
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
    
def clean2():
    remove_noise(DEST_DIR)

# archives the destination folder
def archive():
    logging.info(f"creating archive from {DEST_DIR}")
    __make_archive(f"{DEST_DIR}.tar.gz", DEST_DIR)
    logging.info(f"creat archive from {DEST_DIR}.tar.gz")

# creates the test file for the dataset
def create_test_file():
    datafile_path = f"{DEST_DIR}/datafile.txt"
    testfile_path = f"{DEST_DIR}/testing_list.txt"
    __reset_file("testing_list.txt")
    x_test_datas = [] 
    with open(datafile_path, "rb") as f:
       data = []
       for line in f:
          data.append(line.strip().decode('utf-8'))
       _, x_test_datas = train_test_split(data, test_size=0.3) 
    with open(testfile_path, "a+") as f:
        for x_test_data in x_test_datas:
           f.write(x_test_data + '\n')

def __main(arg):
    if arg == 'clean':
        clean()
    if arg == 'cut':
        cut()
    if arg == 'clean2':
        clean2()
    if arg == 'archive':
        archive()
    if arg == 'testfile':
        create_test_file()

if __name__ == '__main__':
    arg = sys.argv[1]
    if not ("clean" in arg or "cut" in arg or "archive" in arg or "testfile" in arg or "clean2" in arg):
        sys.stderr.write(
            'Usage: preprocess.py <clean | cut | archive | testfile>\n')
        sys.exit(1)
    if len(sys.argv[1:]) != 1:
        sys.stderr.write(
            'Usage: preprocess.py <clean | cut | archive>\n')
        sys.exit(1)
    __main(sys.argv[1])
