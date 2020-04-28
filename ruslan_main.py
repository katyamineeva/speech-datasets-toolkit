import os

import config as cfg
from utils import load_json, dump_json, unify_hyphens, train_val_split_json_to_txt
from filter import filter_filelist

from find_questions import sample_questions_non_questions_filelist

from stress import add_stress_to_one_syllable_words,\
                   remove_stress_where_not_needed,\
                   find_errors_advanced

from balanced_dataset import compute_cover_of_phoneme_combinations,\
                             get_phonetic_statistics_filelist,\
                             filelist_to_phonetic_statistics,\
                             get_representative_sample_greedy


sys.path.append('/mnt/sdb/tacotron2_ann')
from text.dictionary import CMUDict


def create_questions_dataset():
    questions_non_questions_json = os.path.join(cfg.ruslan_path, "questions_non_questions_all.json")
    sample_questions_non_questions_filelist(cfg.all_streesed_filtered_v4_json,
                                            questions_non_questions_json)
    questions_non_questions_folder = os.path.join(cfg.ruslan_path, "questions_non_questions_stressed")

    train_val_split_json_to_txt(questions_non_questions_json, questions_non_questions_folder)


def stress_tuning():
    errors_json = os.path.join(cfg.ruslan_path, "errors_in_stress_v4.json")

    add_stress_to_one_syllable_words(cfg.all_v4_stressed_json, cfg.all_v4_stressed_json)
    remove_stress_where_not_needed(cfg.all_v4_stressed_json, cfg.all_v4_stressed_json)
    find_errors_advanced(cfg.all_v4_stressed_json, errors_json)


def compute_phonetic_statistics():
    cmudict = CMUDict(cfg.cmudict_path)
    get_phonetic_statistics_filelist(cfg.all_v4_stressed_json, cmudict, cfg.all_v4_phoneme_statistics_json)
    filelist_to_phonetic_statistics(cfg.all_v4_phoneme_statistics_json, cfg.phonemes_statistics_ruslan_json)


def create_balanced_sample():
    representative_diphones_json = os.path.join(cfg.ruslan_path, "representative_diphones.json")

    get_representative_sample_greedy(cfg.all_v4_stressed_json,
                                     cfg.all_v4_phoneme_statistics_json,
                                     cfg.wavs_duration,
                                     cfg.phonemes_statistics_ruslan_json,
                                     representative_diphones_json)

    compute_cover_of_phoneme_combinations(representative_diphones_json,
                                          cfg.all_v4_phoneme_statistics_json,
                                          cfg.list_of_phonemes_combinations_json)


if __name__ == '__main__':
    pass