from pathlib import Path
from random import shuffle
from os import stat
import math

def get_min_total_size(file_paths: list[str]) -> int:
    totals = {}
    classes = []
    for sound_file_path in file_paths:
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
    return int(min)



def clamp_data_size(file_paths: list[str], max_size: int) -> list[str]:
    totals = {}
    classes = []
    res = []
    for sound_file_path in file_paths:
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

def ceil_by_min_size(file_paths: list[str]) -> list[str]:
    min_total_size = get_min_total_size(file_paths)
    shuffle(file_paths)
    return clamp_data_size(file_paths, min_total_size)
