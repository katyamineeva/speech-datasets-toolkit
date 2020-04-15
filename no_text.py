import os

import config as cfg
from utils import load_json


def find_no_texts(filelist_json, dataset_path, out_txt):
    wavname_to_text = load_json(filelist_json)

    total_wavs_cnt = 0
    no_text_wavnames = []
    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset",  foldername, "wavs")):
            wavname_original = os.path.join("dataset", foldername, "wavs", filename)
            is_wav = (filename.split(".")[-1] == "wav")
            if is_wav:
                total_wavs_cnt += 1
                if wavname_original not in wavname_to_text:
                    no_text_wavnames.append(wavname_original)

    fout = open(out_txt, "w+")
    fout.write("\n".join(no_text_wavnames))

    print("{} out of {} audios has no corresponding text"
          .format(len(no_text_wavnames), total_wavs_cnt))

    return no_text_wavnames


def main():
    pass


if __name__ == "__main__":
    main()

