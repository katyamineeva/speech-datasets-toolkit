import os
import soundfile
import glob
import shutil

import config as cfg
from utils import load_json, dump_json,\
                  merge_filelists_txt_to_dict,\
                  remove_wavnames_which_not_exist,\
                  merge_dicts,\
                  count_filelist_duration,\
                  filelist_json_to_txt

from renaming import convert_filename, convert_names_filelist_json_to_txt


# def long_wavnames_to_list(dataset_path, out_json):
#     long_wavs = []
#     for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
#         for filename in os.listdir(os.path.join(dataset_path, "dataset", foldername, "wavs")):
#             if filename.split(".")[-1] == "wav":
#                 wavname_original = os.path.join("dataset", foldername, "wavs", filename)
#                 wavpath = os.path.join(dataset_path, "dataset", foldername, "wavs", filename)
#
#                 audio, sample_rate = soundfile.read(wavpath)
#                 duration = audio.shape[0] / sample_rate
#                 if duration > 10:
#                     long_wavs.append(wavname_original)
#
#     dump_json(long_wavs, out_json)
#
#     return long_wavs


def is_one_sentence(text):
    if "." in text:
        return False
    if "?" in text:
        return False
    if "!" in text:
        return False
    return True


def filelist_long_to_dict(filelist_json, wavs_duration_json, exclude_json=None):
    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration_json)

    if exclude_json is not None:
        excluded_wavnames = load_json(exclude_json)
    else:
        excluded_wavnames = set()

    long_dict = {}
    for wavname in wavname_to_text:
        if wavs_duration[wavname] > cfg.max_duration\
            and not is_one_sentence(wavname_to_text[wavname])\
            and wavname not in excluded_wavnames:
            long_dict[wavname] = wavname_to_text[wavname]

    return long_dict


def filelist_long_to_json(filelist_json, wavs_duration_json, out_json, exclude_json=None):
    long_dict = filelist_long_to_dict(filelist_json, wavs_duration_json, exclude_json)
    dump_json(long_dict, out_json)

    print("%d long audios found" % len(long_dict))

    return long_dict


def wavs_in_one_folder(filelist_json, dataset_path, out_folder, rename=True):
    wavs_outpath = os.path.join(out_folder, "wavs")
    if not os.path.exists(wavs_outpath):
        os.makedirs(wavs_outpath)

    if filelist_json is not None:
        target_wavs = load_json(filelist_json)

        for wavname in target_wavs:
            src_path = os.path.join(dataset_path, wavname)

            if rename:
                dst_path = os.path.join(wavs_outpath, convert_filename(wavname))
            else:
                dst_path = os.path.join(wavs_outpath, os.path.basename(wavname))
            shutil.copyfile(src_path, dst_path)
        cnt_wavs = len(target_wavs)
    else:
        cnt_wavs = 0
        for wavpath in glob.glob(os.path.join(dataset_path, "dataset", "**", "*.wav"), recursive=True):
            new_wavname = convert_filename(wavpath.replace(dataset_path, ""))
            dst_path = os.path.join(out_folder, new_wavname)
            shutil.copyfile(wavpath, dst_path)
            cnt_wavs += 1

    print("%d wavs were moved to %s" % (cnt_wavs, out_folder))




def get_chopped_filelist(filelists_txt_folder, all_json,  out_json):
    chopped_unchopped = merge_filelists_txt_to_dict(filelists_txt_folder)
    wavnames_renamed_before_chopping = [convert_filename(wavname) for wavname in load_json(all_json)]
    result = {}

    for wavname in chopped_unchopped:
        if wavname not in wavnames_renamed_before_chopping:
            result[os.path.join("dataset", "chopped", "wavs", wavname)] = chopped_unchopped[wavname]

    dump_json(result, out_json)


def replace_with_chopped_in_filelist(filelist_json, chopped_json, out_json):
    wavname_to_text = load_json(filelist_json)
    chopped = load_json(chopped_json)
    result = {}

    were_chopped = set()
    for wavname in chopped:
        were_chopped.add("_".join(wavname.split("_")[ : -1]) + ".wav")

    for wavname in wavname_to_text:
        if convert_filename(wavname) not in were_chopped:
            result[wavname] = wavname_to_text[wavname]

    result = merge_dicts([result, chopped])
    dump_json(result, out_json)


# def chopped_wavname_to_wavpath(filelist_json, chopped_json):
#     original_filelist = load_json(filelist_json)
#     chopped_unchopped_filelist = load_json(chopped_json)
#     unchopped_wavnames = [convert_filename(wavname) for wavname in original_filelist]
#
#     chopped_filelist = {}
#
#     for wavname in chopped_unchopped_filelist:
#         if wavname not in unchopped_wavnames:
#             wavpath = os.path.join("dataset", "chopped", "wavs", wavname)
#             chopped_filelist[wavpath] = chopped_unchopped_filelist[wavname]
#
#     dump_json(chopped_filelist, chopped_json)


def correct_mistakes_in_unchopped_filelist(unchopped_json, chopped_json, out_json):
    unchopped = load_json(unchopped_json)
    chopped = [os.path.basename(wavpath) for wavpath in load_json(chopped_json)]
    result = {}

    for wavname in unchopped:
        first_part_wavname = convert_filename(wavname).split(".")[0] + "_1.wav"
        if not first_part_wavname in chopped:
            result[wavname] = unchopped[wavname]

    dump_json(result, out_json)
    print("%d mistakes found" % (len(unchopped) - len(result)))


def main():

    pass


if __name__ == "__main__":
    main()
