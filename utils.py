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
        print("Warning! There was a conflict while merging dictionaries:\
              {} keys berfore merge resulted in {} keys".format(src_folder, cnt_initial, cnt_result))

    return result


def filelist_txt_to_dict(filelist_txt):
    assert filelist_txt.split(".")[-1] == "txt" or filelist_txt.split(".")[-1] == "csv"

    wavname_to_text = {}
    for line in open(filelist_txt):
        if line != "\n":
            wavname, text = line.split("|")
            wavname_to_text[wavname] = text

    print(len(wavname_to_text), "found in", filelist_txt)
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


def main():

    pass


if __name__ == "__main__":
    main()
