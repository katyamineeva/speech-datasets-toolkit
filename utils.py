import os
import json
import numpy as np

import config as cfg


def add_suffix(filepath, suffix):
    return os.path.basename(filepath).split(".")[0] + "_" + suffix + filepath.split(".")[-1]


def load_json(json_path):
    assert json_path.split(".")[-1] == "json"

    with open(json_path) as f:
        return json.load(f)


def dump_json(some_object, out_json):
    assert out_json.split(".")[-1] == "json"

    with open(out_json, "w+") as f:
        json.dump(some_object, f, indent=4, ensure_ascii=False)


def merge_dicts(dicts):
    result = {}
    for d in dicts:
        result = {**result, **d}

    cnt_initial = sum(map(len, dicts))
    cnt_result = len(result)

    if cnt_initial != cnt_result:
        print("Warning! There was a conflict while merging dictionaries")
        print("%d keys berfore merge resulted in %d keys, the delta is %d" % (cnt_initial,
                                                                              cnt_result,
                                                                              cnt_initial - cnt_result))

    return result


def filelist_txt_to_dict(filelist_txt):
    assert filelist_txt.split(".")[-1] == "txt" or filelist_txt.split(".")[-1] == "csv"

    wavname_to_text = {}
    for line in open(filelist_txt):
        if line != "\n":
            wavname, text = line.split("|")
            wavname_to_text[wavname] = text

    print(len(wavname_to_text), "found in", os.path.basename(filelist_txt))
    return wavname_to_text


def filelist_txt_to_json(filelist_txt, out_json):
    assert filelist_txt.split(".")[-1] == "txt" or filelist_txt.split(".")[-1] == "csv"

    wavname_to_text = filelist_txt_to_dict(filelist_txt)
    dump_json(wavname_to_text, out_json)

    return  wavname_to_text


def filelist_dict_to_txt(filelist_dict, out_txt):
    assert out_txt.split(".")[-1] == "txt" or out_txt.split(".")[-1] == "csv"

    lines = []
    for wavname in filelist_dict:
        lines.append(wavname + "|" + filelist_dict[wavname].replace("\n", ""))

    open(out_txt, "w+").write('\n'.join(lines))


def filelist_json_to_txt(filelist_json, out_txt):
    assert out_txt.split(".")[-1] == "txt" or out_txt.split(".")[-1] == "csv"

    filelist_dict = load_json(filelist_json)
    filelist_dict_to_txt(filelist_dict, out_txt)


def merge_filelists_txt_to_dict(src_folder):
    list_of_dicts = []
    for filelist_txt_name in os.listdir(src_folder):
        filelist_txt = os.path.join(src_folder, filelist_txt_name)
        list_of_dicts.append(filelist_txt_to_dict(filelist_txt))

    merged_dict = merge_dicts(list_of_dicts)

    return merged_dict


def merge_filelists_txt_to_json(src_folder, out_json):
    merged_filelist_dict = merge_filelists_txt_to_dict(src_folder)
    dump_json(merged_filelist_dict, out_json)

    return merged_filelist_dict


def merge_filelists_jsons_to_json(json_filelists_list, out_json):
    result = merge_dicts([load_json(filelist_json) for filelist_json in json_filelists_list])
    dump_json(result, out_json)


def train_val_split_json_to_txt(filelist_json, dst_folder, val_fraction=0.2):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    wavname_to_text = load_json(filelist_json)
    val_wavnames = np.random.choice(list(wavname_to_text.keys()),
                                    int(val_fraction * len(wavname_to_text)),
                                    replace=False)

    train_wavname_to_text = {}
    val_wavname_to_text = {}

    for wavname in wavname_to_text:
        if wavname in val_wavnames:
            val_wavname_to_text[wavname] = wavname_to_text[wavname]
        else:
            train_wavname_to_text[wavname] = wavname_to_text[wavname]

    filename = os.path.basename(filelist_json).split(".")[0]
    train_txt = os.path.join(dst_folder, "train_" + filename + ".txt")
    val_txt = os.path.join(dst_folder, "val_" + filename + ".txt")

    filelist_dict_to_txt(train_wavname_to_text, train_txt)
    filelist_dict_to_txt(val_wavname_to_text, val_txt)


def count_texts_wavs(dataset_path, filelist_json):
    cnt_audios = 0
    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset",  foldername, "wavs")):
            if filename.split(".")[-1] == "wav":
                cnt_audios += 1

    wavname_to_text = load_json(filelist_json)
    cnt_texts = len(wavname_to_text)

    print("Dataset contains {} audios and {} texts, the difference is {}"
        .format(cnt_audios,cnt_texts, cnt_audios - cnt_texts))


def get_wavs_duration(dataset_path, out_json, start_from_scratch=False):
    if os.path.exists(out_json):
        wavs_duration = load_json(out_json)
    else:
        wavs_duration = {}

    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset", foldername, "wavs")):
            if filename.split(".")[-1] == "wav":
                wavname_original = os.path.join("dataset", foldername, "wavs", filename)
                if wavname_original not in wavs_duration:
                    wavpath = os.path.join(dataset_path, "dataset", foldername, "wavs", filename)

                    audio, sample_rate = soundfile.read(wavpath)
                    wavs_duration[wavname_original] = audio.shape[0] / sample_rate

    dump_json(wavs_duration, out_json)

    return wavs_duration


def count_filelist_duration(filelist_json, wavs_duration_json):
    duration = load_json(wavs_duration_json)
    total_duration = 0
    for wavname in load_json(filelist_json):
        total_duration += duration[wavname]

    total_duration /= 60 * 60
    print("\nTolal duration of %s is %.2f hours\n" % (os.path.basename(filelist_json), total_duration))


def ensure_exactly_one_space_after_punctuation(filelist_json, out_json):
    wavname_to_text = load_json(filelist_json)

    for wavname in wavname_to_text:
        text = wavname_to_text[wavname]
        text = text.replace(",", ", ")
        text = text.replace("?", "? ")
        text = text.replace("!", "! ")
        text = text.replace("...", "... ")
        for s in cfg.russian_letters:
            text = text.replace("." + s, ". " + s)

        wavname_to_text[wavname] = " ".join(text.split())

    dump_json(wavname_to_text, out_json)


def dump_texts_only(filelist_json, out_json):
    dump_json(list(load_json(filelist_json).values()), out_json)


def remove_wavnames_which_not_exist(filelist_json, dataset_path, out_json):
    print("\n" + "=" * 15 + " Removing non existing wavnames from filelist " + "=" * 15)
    print("Processing", os.path.basename(filelist_json), "\n")
    filelist = load_json(filelist_json)
    result = {}
    for wavname in filelist:
        if os.path.exists(os.path.join(dataset_path, wavname)):
            result[wavname] = filelist[wavname]
        else:
            print("Removed:", wavname)

    print("\nRemoved %d wavnames in total, %d left" % (len(filelist) - len(result), len(result)))
    print("=" * 76)
    dump_json(result, out_json)


def main():
    # filelist_json = os.path.join(cfg.filelists_folder, "stress_part_plus_sign.json")
    # out_json = os.path.join(cfg.filelists_folder, "amai_stressed_texts_only.json")
    # all_v4 = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_long.json")
    # all_asr_checked_v4 = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked.json")
    # # dump_texts_only(filelist_json, out_json)
    # remove_wavnames_which_not_exist(all_asr_checked_v4, cfg.amai_path, all_asr_checked_v4)
    chopped_json = os.path.join(cfg.filelists_folder, "chopped.json")
    count_filelist_duration(chopped_json, cfg.wavs_duration_json)
    pass


if __name__ == "__main__":
    main()
