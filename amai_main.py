import os
import config as cfg

from stress import find_errors_in_stress, find_unstressed_texts
from utils import count_filelist_duration, remove_wavnames_which_not_exist, load_json, dump_json, filelist_txt_to_dict,\
                  filelist_dict_to_txt

from filter import filter_filelist
from renaming import convert_names_filelist_json_to_json, convert_names_filelist_json_to_txt
from long_audios import wavs_in_one_folder, exclude_wavs_with_one_sentence

def filter_v4():
    all_v4_with_chopped_asr_checked_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked.json")
    all_v4_with_chopped_asr_checked_filtered_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")

    filter_filelist(all_v4_with_chopped_asr_checked_json,
                    cfg.wavs_duration_json,
                    all_v4_with_chopped_asr_checked_filtered_json,
                    print_long_wavnames=True)

    count_filelist_duration(cfg.all_v3_json, cfg.wavs_duration_json)
    count_filelist_duration(all_v4_with_chopped_asr_checked_json, cfg.wavs_duration_json)
    count_filelist_duration(all_v4_with_chopped_asr_checked_filtered_json, cfg.wavs_duration_json)


def convert_names_v4():
    in_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")
    out_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered_new_names.json")
    convert_names_filelist_json_to_json(in_json, out_json)
    remove_wavnames_which_not_exist(out_json, cfg.all_wavs_folder)


def stress_correction_task_v4():
    in_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")
    exclude_json = os.path.join(cfg.filelists_folder, "long_v4_corrected.json")
    out_json = os.path.join(cfg.filelists_folder, "errors_in_stress_v4.json")

    find_errors_in_stress(in_json, out_json=out_json, exclude_json=exclude_json)


def stress_placement_task_v4():
    in_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")
    exclude_json = os.path.join(cfg.filelists_folder, "long_v4_corrected.json")
    out_json = os.path.join(cfg.filelists_folder, "unstressed_v4.json")
    out_txt = os.path.join(cfg.filelists_folder, "roma", "unstressed_v4.txt")

    find_unstressed_texts(in_json, out_json=out_json, exclude_json=exclude_json)
    convert_names_filelist_json_to_txt(out_json, out_txt)


def long_v4():
    in_json = os.path.join(cfg.filelists_folder, "long_v4_corrected.json")
    out_json = os.path.join(cfg.filelists_folder, "long_v4_corrected_twice.json")
    exclude_wavs_with_one_sentence(in_json, out_json)

    out_folder = os.path.join(cfg.amai_path, "long_with_texts_v4_corrected")
    out_txt = os.path.join(out_folder, "long_v4_corrected_twice.txt")

    wavs_in_one_folder(out_json, cfg.amai_path, out_folder)
    convert_names_filelist_json_to_txt(out_json, out_txt)


def both_sent_to_ira_and_have_to_be_chopped():
    in_txt_1 = os.path.join(cfg.amai_path, "long_with_texts_v4_corrected", "long_v4_corrected_twice.txt")
    in_txt_2 = os.path.join(cfg.filelists_folder, "txts",  "sent_to_ira.txt")
    out_txt = os.path.join(cfg.amai_path, "long_with_texts_v4_corrected", "in_both_lists.txt")

    filelist1 = filelist_txt_to_dict(in_txt_1)
    filelist2 = filelist_txt_to_dict(in_txt_2)

    result = {}
    for wavname in set(filelist1.keys()).intersection(set(filelist2.keys())):
        result[wavname] = filelist2[wavname]

    filelist_dict_to_txt(result, out_txt)

def main():
    # stress_correction_task_v4()
    # stress_placement_task_v4()
    both_sent_to_ira_and_have_to_be_chopped()

if __name__ == '__main__':
    main()
