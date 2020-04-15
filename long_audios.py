import os
import soundfile
import shutil

import config as cfg
from utils import load_json, dump_json, merge_filelists_txt_to_json
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


def replace_long_with_chopped_in_json(filelist_json, chopped_json, out_json):
    wavname_to_text = load_json(filelist_json)
    chopped = load_json(chopped_json)
    result = {}

    wavnames_before_chopping = [convert_filename(wavname) for wavname in wavname_to_text]
    chopped_wavnames_before_chopping = set()
    chopped_wavnames_after_chopping = []

    for wavname in chopped:
        if wavname not in wavnames_before_chopping:
            chopped_wavnames_before_chopping.add("_".join(wavname.split("_")[ : -1]) + ".wav")
            chopped_wavnames_after_chopping.append(wavname)

    for wavname in wavname_to_text:
        if convert_filename(wavname) not in chopped_wavnames_before_chopping:
            result[wavname] = wavname_to_text[wavname]

    for wavname in chopped:
        if wavname in chopped_wavnames_after_chopping:
            result[wavname] = chopped[wavname]

    print(len(chopped_wavnames_before_chopping), "wavs were really chopped")
    dump_json(result, out_json)


def chopped_wavname_to_wavpath(filelist_json, chopped_json):
    original_filelist = load_json(filelist_json)
    chopped_unchopped_filelist = load_json(chopped_json)
    unchopped_wavnames = [convert_filename(wavname) for wavname in original_filelist]

    chopped_filelist = {}

    for wavname in chopped_unchopped_filelist:
        if wavname not in unchopped_wavnames:
            wavpath = os.path.join("dataset", "chopped", "wavs", wavname)
            chopped_filelist[wavpath] = chopped_unchopped_filelist[wavname]

    dump_json(chopped_filelist, chopped_json)


def main():
    # merge long wavs in one folder

    # create filelist with new names
    chopped_filelists_folder = os.path.join(cfg.filelists_folder, "txts", "chopped_long")
    chopped_json = os.path.join(cfg.filelists_folder, "chopped.json")
    all_v4_with_chopped_long_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_long.json")

    merge_filelists_txt_to_json(chopped_filelists_folder, chopped_json)
    replace_long_with_chopped_in_json(cfg.all_v3_json, chopped_json, all_v4_with_chopped_long_json)
    chopped_wavname_to_wavpath(cfg.all_v3_json, chopped_json)
    pass


if __name__ == "__main__":
    main()
