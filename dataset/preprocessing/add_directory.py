from pathlib import Path
from os import path, makedirs

def add_tmp_dir(filepath_str: str, tmp_dir: str):
    filepath = Path(filepath_str)
    filename = filepath.name
    classname = filepath.parent.name
    relative_path = f"{tmp_dir}/{classname}/{filename}"
    absolute_path = path.dirname(__file__) + "/../"
    full_path = path.join(absolute_path, relative_path)
    makedirs(path.dirname(full_path), exist_ok=True)
    return full_path
