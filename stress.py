import os
import config as cfg
from utils import load_json, dump_json, filelist_json_to_txt
from long_audios import wavs_in_one_folder
from renaming import convert_names_filelist_json_to_txt


def get_no_stress_filelist(filelist_json, out_json):
    wavname_to_text = load_json(filelist_json)
    no_stress_wavname_to_text = {}

    for wavname in wavname_to_text:
        if "_processed" not in wavname:
            no_stress_wavname_to_text[wavname] = wavname_to_text[wavname]

    print(len(no_stress_wavname_to_text), "wavs without stress out of", len(wavname_to_text))
    dump_json(no_stress_wavname_to_text, out_json)


def stress_ok(word):
    vowels_count = sum(map(word.lower().count, cfg.vowels_lower))
    uppercase_vowels_count = sum(map(word.count, cfg.vowels_upper))

    if word.lower() in cfg.known_stresses or word.lower() in cfg.no_stress:
        return True

    if "-" in word:
        for subword in word.split("-"):
            if not stress_ok(subword):
                return False
        return True

    if cfg.always_stressed_vowel_lower in word.lower():
        return True
    if uppercase_vowels_count == 0 and vowels_count <= 1:
        return True
    if uppercase_vowels_count == 1:
        return True
    if uppercase_vowels_count == 2 and word[0] in cfg.vowels_upper:
        return True

    return False


def word_uppercase_to_plus(word):
    assert stress_ok(word)

    vowels_count = sum(map(word.count, cfg.all_vowels))
    vowels_indices = [ind for ind, s in enumerate(word) if s in cfg.all_vowels]

    uppercase_vowels_count = sum(map(word.count, cfg.vowels_upper))
    uppercase_vowels_indices = [ind for ind, s in enumerate(word) if s in cfg.vowels_upper]

    if word.lower() in cfg.known_stresses:
        return cfg.known_stresses[word.lower()]

    if "-" in word:
        modified_subwords = []
        for subword in word.split("-"):
            if subword.lower() in cfg.no_stress:
                modified_subwords.append(subword.lower())
            else:
                modified_subwords.append(word_uppercase_to_plus(subword))
        return "-".join(modified_subwords)

    word = word.lower()
    if cfg.always_stressed_vowel_lower in word.lower():
        ind = word.find(cfg.always_stressed_vowel_lower)
        return word[ : ind] + "+" + word[ind : ]

    if uppercase_vowels_count == 0:
        if vowels_count == 0:
            return word
        else:
            return word[ : vowels_indices[0]] + "+" + word[vowels_indices[0] : ]

    if uppercase_vowels_count == 1:
        return word[ : uppercase_vowels_indices[0]] + "+" + word[uppercase_vowels_indices[0] : ]

    if uppercase_vowels_count == 2:
        return word[ : uppercase_vowels_indices[1]] + "+" + word[uppercase_vowels_indices[1] : ]

    return "Something very weird happened"


def filelist_uppercase_to_plus(filelist_json, out_json):
    wavname_to_text = load_json(filelist_json)

    modified_wavname_to_text = {}
    cnt_mistakes = 0
    for wavname in wavname_to_text:
        if "_processed" in wavname:
            modified_text = []
            all_sentence_ok = True
            for word in wavname_to_text[wavname].split():
                if stress_ok(word):
                    modified_text.append(word_uppercase_to_plus(word))
                else:
                    all_sentence_ok = False

            if all_sentence_ok:
                modified_wavname_to_text[wavname] = " ".join(modified_text)
            else:
                cnt_mistakes += 1

    dump_json(modified_wavname_to_text, out_json)

    print("in %d texts stress notation were modified from uppercase to plus, %d have error in stress"\
          % (len(modified_wavname_to_text), cnt_mistakes))


def find_errors_in_stress(filelist_json, out_json=None, exclude_json={}):
    wavname_to_text = load_json(filelist_json)
    exclude = load_json(exclude_json)

    errors = {}
    for wavname in wavname_to_text:
        if "_processed" in wavname and wavname not in exclude:
            modified_text = []
            sentence_ok = True
            for word in wavname_to_text[wavname].split():
                if stress_ok(word):
                    modified_text.append(word_uppercase_to_plus(word))
                else:
                    sentence_ok = False
                    modified_text.append(word)
                    if wavname in errors:
                        errors[wavname]["errors"].append(word)
                    else:
                        errors[wavname] = {"text": None, "errors" : [word]}

            if not sentence_ok:
                errors[wavname]["text"] = " ".join(modified_text)

    if out_json is not None:
        dump_json(errors, out_json)

    print(len(errors), "errors were found in stress marking")


def find_unstressed_texts(filelist_json, out_json, exclude_json={}):
    wavname_to_text = load_json(filelist_json)
    exclude = load_json(exclude_json)

    result = {}
    for wavname in wavname_to_text:
        if wavname not in exclude:
            if "_processed" not in wavname:
                result[wavname] = wavname_to_text[wavname]

    if out_json is not None:
        dump_json(result, out_json)

    print(len(result), "unstreesed texts found")
