import os
import librosa
import soundfile

import config as cfg 


def convert_sample_rate(rpath, wpath):
    files = os.listdir(rpath)
    for i, filename in enumerate(files):
        filepath = os.path.join(rpath, filename)
        y, sr = librosa.load(filepath, sr=44100 // 2)

        print("\rProcessed {} out of {} with sr {} and length {}".format(i + 1, len(files), sr, len(y) / sr), end="")

        os.makedirs(wpath, exist_ok=True)
        librosa.output.write_wav(os.path.join(wpath, filename), y, sr)


def float_to_int16(rpath, wpath):
    os.makedirs(wpath, exist_ok=True)
    files = os.listdir(rpath)
    for i, filename in enumerate(files):
        filepath = os.path.join(rpath, filename)
        y, sr = librosa.load(filepath, sr=44100 // 2)
        print("\rProcessed {} out of {} with sr {} and length {}".format(i + 1, len(files), sr, len(y) / sr), end="")

        soundfile.write(os.path.join(wpath, filename), y, sr, 'PCM_16')
    print()


def main():



if __name__ == "__main__":
    main()