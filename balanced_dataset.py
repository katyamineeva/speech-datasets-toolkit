import os
import sys
from collections import Counter

import config as cfg
from utils import load_json, dump_json, remove_all_non_letters, sum_of_dicts
from filter import  filter_filelist


def transcribe_filelist(filelist_json, transcriptions_dict, out_json, print_progress=True):
    print(f"--------------- transcription of {os.path.basename(filelist_json)} started ---------------\n")

    wavname_to_text = load_json(filelist_json)
    result = {}

    for wavname in wavname_to_text:
        transcribed_words = []
        cleared_text = remove_all_non_letters(wavname_to_text[wavname],
                                              remove_hyphen=False,
                                              remove_stress_sign=False).lower()
        for word in cleared_text.split():
            phonemes_list = transcriptions_dict.convert_text(word, stress=True, phonemes=True, dict_prime=False)

            if len(phonemes_list) == 0:
                print(f"error! phonemes list is empty\nwavname: {wavname}\ntext: {wavname_to_text[wavname]}\n")

            while phonemes_list[-1] in [" ", "\n", ""]:
                phonemes_list.pop()
                if len(phonemes_list) == 0:
                    print(f"error! phonemes list is empty\nwavname: {wavname}\ntext: {wavname_to_text[wavname]}\n")

            transcribed_words.append("_".join(phonemes_list))

        result[wavname] = " ".join(transcribed_words)
        if print_progress:
            print("\r%.2f%% done" % (len(result) / len(wavname_to_text) * 100), end="")


    dump_json(result, out_json)
    print(f"\rtranscribed filelist {os.path.basename(filelist_json)}\n")


def text_to_phoneme_statistics(text,
                               transcriptions_dict,
                               max_phonemes_number=cfg.max_phonemes_number_in_combination,
                               print_status=False):
    if print_status:
        print("---------------- text_to_phoneme_statistics started ----------------")
    cleaned_text = remove_all_non_letters(text, remove_stress_sign=False, remove_hyphen=False).lower()

    transcribed_list = transcriptions_dict.convert_text(cleaned_text, stress=True, phonemes=True, dict_prime=False)
    redundant_phonemes = [" ", "\n", ""]

    if len(transcribed_list) == 0:
        print(f"error! transcribed list is empty\ntext: {text}")
    while transcribed_list[-1] in redundant_phonemes:
        transcribed_list.pop()
        if len(transcribed_list) == 0:
            print(f"error! transcribed list is empty\ntext: {text}")

    frequencies = Counter(transcribed_list)
    for s in redundant_phonemes:
        if s in frequencies:
            del frequencies[s]

    cnt = 0
    for combination_len in range(2, max_phonemes_number + 1):
        for ind_start in range(len(transcribed_list) - combination_len + 1):
            combination = []
            for ind in range(ind_start, ind_start + combination_len):
                combination.append(transcribed_list[ind])

            if set(combination).isdisjoint(redundant_phonemes):
                frequencies["_".join(combination)] += 1
            cnt += 1
            if print_status:
                print("\r%.2f done" % (cnt / (max_phonemes_number - 1) / len(transcribed_list)), end="")
    if print_status:
        print("\rdone!")
    return frequencies


def get_phonetic_statistics_filelist(filelist_json, transcriptions_dict, out_json, print_progress=True):
    print(f"-------- computing filelist with phoneme statistics for {os.path.basename(filelist_json)} started --------\n")

    wavname_to_text = load_json(filelist_json)
    result = {}
    cnt = 0
    for wavname in wavname_to_text:
        result[wavname] = text_to_phoneme_statistics(wavname_to_text[wavname], transcriptions_dict)
        cnt += 1
        if print_progress:
            print("\r%.2f%% done" % (cnt / len(wavname_to_text) * 100), end="")

    dump_json(result, out_json)
    print(f"\rcomputed filelist with phonemes statistics for {os.path.basename(filelist_json)}\n")


def filelist_to_phonetic_statistics(filelist_json, out_json):
    print(f"------------- computing statistics for the whole {os.path.basename(filelist_json)}")
    wavname_to_statistics = load_json(filelist_json)
    result = sum_of_dicts(wavname_to_statistics.values())
    dump_json(result, out_json)
    print(f"computed phonemes statistics of {os.path.basename(filelist_json)}filelist\n")


def filter_fixed_length_combinations(statistics, target_length):
    result = statistics.copy()
    if isinstance(statistics, dict):
        all_phoneme_combinations = set(statistics.keys())
        for phonemes_combination in all_phoneme_combinations:
            if phonemes_combination.count("_") != target_length - 1:
                del result[phonemes_combination]

    elif isinstance(statistics, set):
        all_phoneme_combinations = statistics
        for phonemes_combination in all_phoneme_combinations:
            if phonemes_combination.count("_") != target_length - 1:
                result.remove(phonemes_combination)
    else:
        raise TypeError(f"expected dict or set, but {type(statistics)} given")

    return result


def get_representative_sample_greedy(filelist_json,
                                     filelist_statistics_json,
                                     wavs_duration_json,
                                     phonemes_statistics_ruslan_json,
                                     out_json,
                                     target_duration=20,
                                     phoneme_combination_length=2,
                                     print_progress=True):
    print("-------------------- greedy algorithm for representative sample --------------------\n")
    print(f"note that only combinations of phonemes of length {phoneme_combination_length} are considered\n")
    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration_json)
    wavname_to_statistics = filter_filelist(filelist_statistics_json,
                                            wavs_duration_json,
                                            max_duration=10,
                                            min_duration=5,
                                            min_len=0)

    print()
    # only phoneme combinations of given length
    target_statistics = filter_fixed_length_combinations(load_json(phonemes_statistics_ruslan_json),
                                                         phoneme_combination_length)
    total_number_of_phonemes = len(target_statistics)

    selected_wavs = set()
    selected_duration = 0
    unselected_phonemes_combinations = set(target_statistics.keys())

    while len(unselected_phonemes_combinations) != 0 and selected_duration < target_duration * 60:
        best_cover_weight = 0
        best_wavname_to_add = None

        for wavname in wavname_to_statistics:
            if wavname not in selected_wavs:
                cur_phonemes_combinations = set(wavname_to_statistics[wavname].keys())
                cur_cover_weight = 0
                for phoneme_combination in unselected_phonemes_combinations.intersection(cur_phonemes_combinations):
                    cur_cover_weight += target_statistics[phoneme_combination]

                if best_wavname_to_add is None or best_cover_weight < cur_cover_weight:
                    best_cover_weight = cur_cover_weight
                    best_wavname_to_add = wavname

        selected_wavs.add(best_wavname_to_add)
        selected_duration += wavs_duration[best_wavname_to_add]
        covered_phonemes_combinations = set(wavname_to_statistics[best_wavname_to_add].keys())
        unselected_phonemes_combinations = unselected_phonemes_combinations.difference(covered_phonemes_combinations)

        if print_progress:
            print("\rduration of selected wavs is %0.2f minutes, covered %d phoneme combinations"
                  % (selected_duration / 60, total_number_of_phonemes - len(unselected_phonemes_combinations)), end="")

    result = {}
    for wavname in selected_wavs:
        result[wavname] = wavname_to_text[wavname]
    dump_json(result, out_json)

    print("\rselected wavs with total duration %0.2f minutes, and %d uncovered phonemes"
          % (selected_duration / 60, len(unselected_phonemes_combinations)))


def get_set_of_covered_phoneme_combinations(wavname_to_statistics, all_phonemes_combinations_list_json, print_info=False):
    result = set()
    for wavname in wavname_to_statistics:
        result = result.union(set(wavname_to_statistics[wavname]))

    all_phonemes_combinations = set(load_json(all_phonemes_combinations_list_json))
    covered_phonemes = all_phonemes_combinations.intersection(result)

    if print_info:
        print("\n%0.2f%% of phonemes combinations are covered by %s\n" %
              (len(covered_phonemes) / len(all_phonemes_combinations) * 100, os.path.basename(wavname_to_statistics)))

    return result


def compute_cover_of_phoneme_combinations(selected_json,
                                          filelist_statistics_json,
                                          all_phonemes_combinations_list_json):
    print("-------------- statistics of coverage of phonemes combinations of fixed size --------------\n")

    wavname_to_statistics = load_json(filelist_statistics_json)
    selected_statistics = {wavname : wavname_to_statistics[wavname] for wavname in load_json(selected_json)}
    covered_phonemes_combinations = get_set_of_covered_phoneme_combinations(selected_statistics,
                                                                            all_phonemes_combinations_list_json)
    all_phonemes_combinations = set(load_json(all_phonemes_combinations_list_json))

    max_len_of_combination = max([max([combination.count("_") + 1 for combination in wavname_to_statistics[wavname]])
                                  for wavname in wavname_to_statistics])

    for target_length in range(1, max_len_of_combination + 1):
        target_combinations = filter_fixed_length_combinations(all_phonemes_combinations, target_length)
        covered_target_combinations = target_combinations.intersection(covered_phonemes_combinations)
        print("%s represents %0.2f%% of combinations of phonemes of length %d"
              % (os.path.basename(selected_json),
                 len(covered_target_combinations) / len(target_combinations) * 100,
                 target_length))
    print()
