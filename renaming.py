import os

import config as cfg
from utils import load_json, dump_json, filelist_txt_to_dict, filelist_dict_to_txt


def convert_foldername(foldername):
    new_name = foldername.replace(" ", "_")
    new_name = new_name.replace("-", "_")
    new_name = new_name.replace("&", "_")
    new_name = new_name.replace("'", "_")
    return new_name


def convert_filename(*args):
    assert 1 <= len(args) <= 2

    if len(args) == 1:
        filepath = args[0]
        filename = filepath.split("/")[-1]
        foldername = filepath.split("/")[-3]
    else:
        foldername, filename = args

    return convert_foldername(foldername) + "-" + filename


def convert_wavnames(dataset_path, out_json):
    filenames_correspondence = {}

    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset",  foldername, "wavs")):
            wavname_original = os.path.join("dataset", foldername, "wavs", filename)
            wavname_new = convert_filename(foldername, filename)
            filenames_correspondence[wavname_new] = wavname_original

    dump_json(filenames_correspondence, out_json)


def convert_names_filelist_dict_to_dict(initial_wavname_to_text, wavnames_correspondence_json=None):
    converted_wavname_to_text = {}
    if wavnames_correspondence_json is not None:
        wavnames_correspondence = load_json(wavnames_correspondence_json)

    for wavname in initial_wavname_to_text:
        if wavnames_correspondence_json is None:
            converted_wavname = convert_filename(wavname)
        else:
            converted_wavname = wavnames_correspondence[wavname]

        converted_wavname_to_text[converted_wavname] = initial_wavname_to_text[wavname]

    return converted_wavname_to_text


def convert_names_filelist_json_to_txt(filelist_json, out_txt, wavnames_correspondence_json=None):
    initial_filelist = load_json(filelist_json)
    converted_filelist = convert_names_filelist_dict_to_dict(initial_filelist, wavnames_correspondence_json)
    filelist_dict_to_txt(converted_filelist, out_txt)


def convert_names_filelist_txt_to_json(filelist_txt, out_json, wavnames_correspondence_json=None):
    initial_filelist = filelist_txt_to_dict(filelist_txt)
    converted_filelist = convert_names_filelist_dict_to_dict(initial_filelist, wavnames_correspondence_json)
    dump_json(converted_filelist, out_json)


def wav_id_to_wavname_ruslan(wav_id):
    return wav_id + "_RUSLAN.wav"


def rename_filelist(filelist_json, out_json):
    wav_id_to_text = load_json(filelist_json)
    wavname_to_text = {}
    for wav_id in wav_id_to_text:
        wavname_to_text[wav_id_to_wavname_ruslan(wav_id)] = wav_id_to_text[wav_id]

    dump_json(wavname_to_text, out_json)


def main():
    out_json = os.path.join(cfg.ruslan_path, "all_v4_streed.json")
    rename_filelist(cfg.all_streesed_v4_json, out_json)
    pass


if __name__ == "__main__":
    main()
