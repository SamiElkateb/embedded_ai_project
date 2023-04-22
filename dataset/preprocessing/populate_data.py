from pathlib import Path
from os import path
from preprocessing import file_shasum

def populate_dest_data(sound_file_paths: list[str]):
    result_array = []
    for sound_file_path in sound_file_paths:
        _, extension = path.splitext(sound_file_path)
        filename = file_shasum(sound_file_path) + extension
        filepath = Path(sound_file_path)
        dirname = filepath.parent.name
        result_array.append({
            "curr_path": sound_file_path,
            "dest_filename": filename,
            "dest_dirname": dirname,
        })
    return result_array

