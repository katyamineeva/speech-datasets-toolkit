import os
import soundfile
import shutil

import config as cfg
from utils import load_json, dump_json
from renaming import convert_filename, convert_names_filelist_json_to_txt


def long_wavnames_to_list(dataset_path, out_json):
    long_wavs = []
    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset", foldername, "wavs")):
            if filename.split(".")[-1] == "wav":
                wavname_original = os.path.join("dataset", foldername, "wavs", filename)
                wavpath = os.path.join(dataset_path, "dataset", foldername, "wavs", filename)

                audio, sample_rate = soundfile.read(wavpath)
                duration = audio.shape[0] / sample_rate
                if duration > 10:
                    long_wavs.append(wavname_original)

    dump_json(long_wavs, out_json)

    return long_wavs


def filelist_long_to_dict(filelist_json, long_list_json, exclude_json=None):
    wavname_to_text = load_json(filelist_json)
    long_wavnames = set(load_json(long_list_json))

    if exclude_json is not None:
        excluded_wavnames = load_json(exclude_json)
    else:
        excluded_wavnames = set()

    long_dict = {}
    for wavname in wavname_to_text:
        if wavname in long_wavnames and wavname not in excluded_wavnames:
            long_dict[wavname] = wavname_to_text[wavname]

    return long_dict


def filelist_long_to_json(filelist_json, long_list_json, out_json, exclude_json=None):
    long_dict = filelist_long_to_dict(filelist_json, long_list_json, exclude_json)
    dump_json(long_dict, out_json)

    return long_dict


def wavs_in_one_folder(filelist_json, dataset_path, out_folder):
    wavs_outpath = os.path.join(out_folder, "wavs")
    if not os.path.exists(wavs_outpath):
        os.makedirs(wavs_outpath)

    target_wavs = load_json(filelist_json)

    for wavname in target_wavs:
        src_path = os.path.join(dataset_path, wavname)
        dst_path = os.path.join(wavs_outpath, convert_filename(wavname))
        shutil.copyfile(src_path, dst_path)


def main():


    # long_wavnames_to_list(cfg.amai_path, long_wavs_list_v2_json) #ignoreline    






    # merge long wavs in one folder

    # create filelist with new names


if __name__ == "__main__":
    main()
