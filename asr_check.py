import requests
import json
import os
from textdistance import levenshtein

import config as cfg
from utils import load_json, dump_json


def recognise_speech(audio_path):
    payload = {'model_type': 'ASR', 'filename': cfg.asr_filename}
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


def find_texts_distortion_in_texts(dataset_path,
                                   filelist_json,
                                   texts_defects_json,
                                   recoginition_errors_json,
                                   start_from_scratch=False):
    wavname_to_text = load_json(filelist_json)

    if os.path.exists(texts_defects_json) and not start_from_scratch:
        texts_distortion = load_json(texts_defects_json)
    else:
        texts_distortion = {}

    recognition_errors = []
    cnt = 0
    max_cnt = len(wavname_to_text)

    for wavname in wavname_to_text:
        cnt += 1
        if cnt > max_cnt:
            break

        if start_from_scratch or wavname not in texts_distortion:
            wav_path = os.path.join(dataset_path, wavname)
            recognised_successfully = False
            try:
                recognised_text = recognise_speech(wav_path)
                recognised_successfully = True
                dist = relative_levenstain(wavname_to_text[wavname], recognised_text)
                texts_distortion[wavname] = {"original" : wavname_to_text[wavname],
                                             "original_unified" : unify_text(wavname_to_text[wavname]),
                                             "recognised" : recognised_text,
                                             "relative_levenshtein" : dist}
                dump_json(texts_distortion, texts_defects_json)
            except:
                if recognised_successfully:
                    ret_val = recognised_text
                else:
                    ret_val = "fail during recognition"
                recognition_errors.append((wav_path, ret_val))
                dump_json(recognition_errors, recoginition_errors_json)



        print("\r%.2f%% completed" % (cnt / max_cnt * 100), end='')
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
    #
    #

    pass


if __name__ == '__main__':
    main()