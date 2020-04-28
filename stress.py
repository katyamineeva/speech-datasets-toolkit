import os

import config as cfg
from utils import load_json, dump_json, remove_all_non_letters


def check_stress_placement(stress_json, mistakes_json, mistakes_filelist_json):
    d = load_json(stress_json) 

    mistakes = []
    ids_of_mistakes = []
    cnt_bad_mistakes = 0
    for item in d:
        mistake_found = False
        bad_mistake_found = False
        item["errors"] = []
        for word in remove_all_non_letters(item["text"], remove_stress_sign=False, remove_hyphen=False).lower().split():
            vowels_count = sum(map(word.lower().count, cfg.vowels_lower))
            if word.count("+") > 1 or (word.count("+") < 1 and vowels_count > 1)\
               and word != "таки" and word != "нибудь" and word != "либо":
                item["errors"].append(word)
                mistake_found = True
                if word[0].lower() == word[0]:
                    bad_mistake_found = True

        if mistake_found:
            mistakes.append(item)
            ids_of_mistakes.append(item["text_id"])
        if bad_mistake_found:
            cnt_bad_mistakes += 1

    if len(mistakes) > 0:
        dump_json(mistakes, mistakes_json)
        dump_json(ids_of_mistakes, mistakes_filelist_json)

    print("{} mistakes out of {} entries. At least {} of them are not names"\
           .format(len(mistakes), len(d), cnt_bad_mistakes))


def emphas_list_to_dict(list_json, out_dict_json):
    info_list = load_json(list_json)
    info_dict = {}

    for item in info_list:
        info_dict[item["text_id"]] = item["text"]

    dump_json(info_dict, out_dict_json)


# first dictionary -- lowest priorty, last -- maximum priority
def render_corrections(jsons_list, out_json):
    lists = []
    for path_json in jsons_list:
        lists.append(load_json(path_json))

    rendered = {}
    for d in lists:
        for item in d:
            rendered[item["text_id"]] = item["text"]

    result = []
    for text_id in rendered:
        result.append({"text_id" : text_id, "text" : rendered[text_id]})

    dump_json(result, out_json)


def add_stress_to_one_syllable_words(in_json, out_json):
    print("----------------------- adding stress to one syllable words -----------------------")
    wavname_to_text = load_json(in_json)

    result = {}
    cnt_corrected = 0
    for wavname in wavname_to_text:
        processed = []
        for word in wavname_to_text[wavname].split():
            vowels_count = sum(map(word.lower().count, cfg.vowels_lower))
            vowels_indices = [ind for ind, s in enumerate(word) if s in cfg.all_vowels]

            if cfg.stress_sign not in word and vowels_count == 1:
                vowel_index = vowels_indices[0]
                word = word[ : vowel_index] + cfg.stress_sign + word[vowel_index : ]
                cnt_corrected += 1

            processed.append(word)
        result[wavname] = " ".join(processed)

    dump_json(result, out_json)
    print(f"processed {len(wavname_to_text)} texts, added stress to {cnt_corrected} words\n")


def correct_stress_in_word_with_hyphen(word):
    assert cfg.hyphen_sign in word

    modified_subwords = []
    for subword in word.split("-"):
        if remove_all_non_letters(subword).lower().replace(cfg.stress_sign, "") in cfg.no_stress_subword:
            subword = subword.replace(cfg.stress_sign, "")
        modified_subwords.append(subword)

    return cfg.hyphen_sign.join(modified_subwords)


def remove_stress_where_not_needed(in_json, out_json, print_corrections=False):
    print("----------------------- removing stress where it's not needed -----------------------\n")

    wavname_to_text = load_json(in_json)

    result = {}
    cnt_corrected = 0
    for wavname in wavname_to_text:
        processed = []
        for word in wavname_to_text[wavname].split():
            if cfg.hyphen_sign in word:
                if correct_stress_in_word_with_hyphen(word) != word:
                    if print_corrections:
                        print(f"wavname: {wavname}\ntext: {wavname_to_text[wavname]}\ncorrected word: {word}\n")
                    word = correct_stress_in_word_with_hyphen(word)
                    cnt_corrected += 1
            else:
                vowels_count = sum(map(word.lower().count, cfg.vowels_lower))
                if vowels_count == 0 and cfg.stress_sign in word:
                    if print_corrections:
                        print(f"wavname: {wavname}\ntext: {wavname_to_text[wavname]}\ncorrected word: {word}\n")
                    word = word.replace(cfg.stress_sign, "")
                    cnt_corrected += 1
            processed.append(word)

        result[wavname] = " ".join(processed)

    dump_json(result, out_json)
    print(f"processed {len(wavname_to_text)} texts, corrected {cnt_corrected} words\n")


def stress_in_word_ok(word):
    vowels_count = sum(map(word.lower().count, cfg.vowels_lower))
    if vowels_count == 0:
        return cfg.stress_sign not in word

    if cfg.hyphen_sign in word:
        for subword in word.split(cfg.hyphen_sign):
            if remove_all_non_letters(subword).lower().replace(cfg.stress_sign, "") in cfg.no_stress_subword:
                if cfg.stress_sign in subword:
                    return False
            elif not stress_in_word_ok(subword):
                return False
        if cfg.stress_sign not in word:
            return False
        return True

    if word.count(cfg.stress_sign) != 1:
        return False

    word = remove_all_non_letters(word, remove_stress_sign=False, remove_hyphen=False)
    if word[-1] == cfg.stress_sign:
        return False

    stress_index = word.find(cfg.stress_sign)
    if word[stress_index + 1].lower() not in cfg.vowels_lower:
        return False

    return True


def find_errors_advanced(in_json, out_json):
    print("------------------------- checking stress placement -------------------------\n")

    wavname_to_text = load_json(in_json)

    errors = {}
    for wavname in wavname_to_text:
        for word in wavname_to_text[wavname].split():
            if not stress_in_word_ok(word):
                if wavname in errors:
                    errors[wavname]["errors"].append(word)
                else:
                    errors[wavname] = {"text": wavname_to_text[wavname],
                                       "errors": [word]}
    dump_json(errors, out_json)
    print(f"\nprocessed {len(wavname_to_text)} texts, found {len(errors)} errors")