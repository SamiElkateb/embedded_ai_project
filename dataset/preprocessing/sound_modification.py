from mutagen.wave import WAVE
from pydub import AudioSegment
from os import path, makedirs

def split_sound(sound_data, absolute_dest_path: str, data_filename: str):
    curr_path = sound_data["curr_path"]
    dest_dirname = sound_data['dest_dirname']
    dest_filename, extension = path.splitext(sound_data['dest_filename'])
    audio_length = int(WAVE(curr_path).info.length)
    audio = AudioSegment.from_wav(curr_path)

    data_filepath = f"{absolute_dest_path}/{data_filename}"

    with open(data_filepath,"a+") as file:
        for i in range(audio_length):
            t1 = i * 1000
            t2 = t1 + 1000
            cut_audio = audio[t1:t2]
            curr_dest_path = f"{absolute_dest_path}/{dest_dirname}/{dest_filename}_{i}{extension}"
            makedirs(path.dirname(curr_dest_path), exist_ok=True)
            cut_audio.export(curr_dest_path, format="wav")
            file.write(f'{dest_dirname}/{dest_filename}_{i}{extension}\n')
