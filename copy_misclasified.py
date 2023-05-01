from os import makedirs, remove, walk, path
from pathlib import Path
from shutil import copyfile

from preprocessing.add_directory import add_tmp_dir


DEST_DIR = "misclasified"

misclasified_list = []
with open('./dataset_v2/misclassified_data.txt', 'r') as misclasified_file:
    # misclasified_list = misclasified_file.readlines()
    for line in misclasified_file:
        misclasified_list.append(line.strip())
for i, filepath in enumerate(misclasified_list):
    dest_path = add_tmp_dir(filepath, DEST_DIR)
    makedirs(path.dirname(dest_path), exist_ok=True)

    absolute_path = path.dirname(__file__)
    full_path = path.join(absolute_path, filepath.replace('./dataset/', ''))
    remove(full_path)

