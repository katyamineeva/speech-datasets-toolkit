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

    if word.lower() in cfg.known_stresses:
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

    if "-" in word:
        modified_subwords = []
        for subword in word.split("-"):
            if subword.lower() in cfg.known_stresses:
                subword = cfg.known_stresses[subword.lower()]
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
    for wavname in wavname_to_text:
        if "_processed" in wavname:
            modified_text = []
            all_sentence_ok = True
            for word in wavname_to_text[wavname].split():
                if stress_ok(word):
                    modified_text.append(word_uppercase_to_plus(word))

            if all_sentence_ok:
                modified_wavname_to_text[wavname] = " ".join(modified_text)

    dump_json(modified_wavname_to_text, out_json)

    print("in %d texts stress notation were modified from uppercase to plus"\
          % len(modified_wavname_to_text))


def filelist_find_errors_in_stress(filelist_json, out_json):
    wavname_to_text = load_json(filelist_json)

    errors = {}
    for wavname in wavname_to_text:
        if "_processed" in wavname:
            for word in wavname_to_text[wavname].split():
                if not stress_ok(word):
                    if wavname in errors:
                        errors[wavname]["errors"].append(word)
                    else:
                        errors[wavname] = {"text" : wavname_to_text[wavname], "errors" : [word]}

    dump_json(errors, out_json)

    print(len(errors), "errors were found in stress marking")


def main():
    # no_stress_json = os.path.join(cfg.filelists_folder, "no_stress.json")  # ignoreline
    # no_stress_folder = os.path.join(cfg.amai_path, "no_stress")  # ignoreline
    # filelist_in_no_stress_folder_txt = os.path.join(no_stress_folder, "no_stress.txt")  # ignoreline
    #
    # get_no_stress_filelist(all_v3_json, no_stress_json)  # ignoreline
    # wavs_in_one_folder(all_v3_json, cfg.amai_path, no_stress_folder)  # ignoreline
    # convert_names_filelist_json_to_txt(no_stress_json, filelist_in_no_stress_folder_txt)  # ignoreline

    errors_in_stress_json = os.path.join(cfg.filelists_folder, "errors_in_stress.json") # ignoreline
    filelist_uppercase_stress_json = os.path.join(cfg.filelists_folder, "uppercase_stress_part.json") # ignoreline
    filelist_uppercase_to_plus(cfg.all_v3_json, filelist_uppercase_stress_json) # ignoreline
    filelist_find_errors_in_stress(cfg.all_v3_json, errors_in_stress_json) # ignoreline
    pass


if __name__ == "__main__":
    main()
