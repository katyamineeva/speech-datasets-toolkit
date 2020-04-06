import requests
import json
import os
from textdistance import levenshtein

import config as cfg
from utils import load_json, dump_json


def recognise_speech(audio_path):
    payload = {'model_type': 'ASR', 'filename': cnf.asr_filename}
    files = [('audio_blob', open(audio_path, 'rb'))]

    headers = {'Authorization': cfg.asr_autorization_str}

    response = requests.request("POST", cfg.asr_api_url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        try:
            return json.loads(response.text)['r'][0]['response'][0]['text'].strip()
        except:
            print(audio_path, response.status_code)
            return False
        else:
            print(audio_path, response.status_code)
            return False


def remove_all_punctuation(text):
    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = text.replace("!", " ")
    text = text.replace("?", " ")
    text = text.replace(":", " ")
    text = text.replace(";", " ")
    text = text.replace("\"", " ")
    text = text.replace(" - ", " ")
    text = text.replace("\\\"", " ")

    return text


def unify_text(text):
    text = text.lower()
    text = remove_all_punctuation(text)
    text = text.replace("\n", " ")
    text = text.replace("ё", "e")
    text = " ".join(text.split())
    # numbers ???

    return text


def relative_levenstain(s1, s2):
    s1 = unify_text(s1)
    s2 = unify_text(s2)

    return levenshtein(s1, s2) / max(len(s1), len(s2))


def find_tests_distortion_in_texts(dataset_path, filelist_json, out_json):
    wavname_to_text = load_json(filelist_json)

    tests_distortion = {}
    cnt = 0
    max_cnt = len(wavname_to_text)
    for wavname in wavname_to_text:
        cnt += 1
        if cnt > max_cnt:
            break
        wav_path = os.path.join(dataset_path, wavname)
        recognised_text = recognise_speech(wav_path)
        dist = relative_levenstain(wavname_to_text[wavname], recognised_text)
        tests_distortion[wavname] = {"original" : wavname_to_text[wavname],
                                     "original_unified" : unify_text(wavname_to_text[wavname]),
                                     "recognised" : recognised_text,
                                     "relative_levenshtein" : dist}

        print("\r%.2f%% completed" % (cnt / max_cnt * 100), end='')
        dump_json(tests_distortion, out_json)
    print("\rdone!            ")


def find_errors(distortions_path, errors_json):
    distortions = load_json(distortions_path)
    errors = {}
    for wavname in distortions:
        if len(distortions[wavname]["original"]) > 10\
           and distortions[wavname]["relative_levenshtein"] > cfg.levenshtein_dist_threshold:

            errors[wavname] = distortions[wavname]
            del errors[wavname]["original"]

    print("{} texts out of {} differ from recognised ones by {}% or more"\
           .format(len(errors), len(distortions), int(cfg.levenshtein_dist_threshold * 100)))

    dump_json(errors, errors_json)


def main():
    filelist_json = os.path.join(cfg.filelists_folder, "all_v2.json") #ignoreline
    distortions_json = os.path.join(cfg.filelists_folder, "tests_distortion.json") #ignoreline
    part_distortions_json = os.path.join(cfg.filelists_folder, "tests_distortion_part.json") #ignoreline
    errors_json = os.path.join(cfg.filelists_folder, "errors.json") #ignoreline

    # find_tests_distortion_in_texts(cfg.amai_path, filelist_json, distortions_json) #ignoreline
    find_errors(part_distortions_json, errors_json) #ignoreline

    pass


if __name__ == '__main__':
    main()