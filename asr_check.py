import requests
import json
import os
from textdistance import levenshtein

import config as cfg
from utils import load_json, dump_json, merge_filelists_jsons_to_json
from long_audios import wavs_in_one_folder


def recognise_speech(audio_path):
    payload = {'model_type': cfg.asr_model_type,
               'filename': cfg.asr_filename,
               'username' : cfg.asr_username,
               'token' : cfg.asr_token}

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


def recognise_filelist(dataset_path,
                       filelist_json,
                       texts_distortions_json,
                       recoginition_errors_json,
                       start_from_scratch=False):

    wavname_to_text = load_json(filelist_json)

    if os.path.exists(texts_distortions_json) and not start_from_scratch:
        texts_distortion = load_json(texts_distortions_json)
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
                dump_json(texts_distortion, texts_distortions_json)
            except:
                if recognised_successfully:
                    ret_val = recognised_text
                else:
                    ret_val = "fail during recognition"
                recognition_errors.append((wav_path, ret_val))
                dump_json(recognition_errors, recoginition_errors_json)



        print("\r%.2f%% completed" % (cnt / max_cnt * 100), end='')
    print("\rdone!            ")


def find_errors(distortions_path, errors_json, exclude_json=None):
    distortions = load_json(distortions_path)
    errors = {}
    exclude = {}
    if exclude_json is not None:
        exclude = load_json(exclude_json)

    for wavname in distortions:
        if len(distortions[wavname]["original"]) > 10 and wavname not in exclude\
           and distortions[wavname]["relative_levenshtein"] > cfg.levenshtein_dist_threshold:
            errors[wavname] = distortions[wavname]
            del errors[wavname]["original_unified"]

    print("{} texts out of {} differ from recognised ones by {}% or more"\
           .format(len(errors), len(distortions), int(cfg.levenshtein_dist_threshold * 100)))

    dump_json(errors, errors_json)


def correct_confirmed_errors_in_filelist(confirmed_errors_json):
    errors = load_json(confirmed_errors_json)
    corrected = {}
    for wavname in errors:
        corrected[wavname] = errors[wavname]["ground_truth"]

    dump_json(corrected, confirmed_errors_json)


def main():
    # texts_distortion_json = os.path.join(cfg.filelists_folder, "texts_distortion.json")
    # recognition_errors_json = os.path.join(cfg.filelists_folder, "recognition_errors.json")
    # # exclude_json = os.path.join(cfg.filelists_folder, "errors_asr_vs_texts_v2.json")
    # # errors_asr_vs_texts_v3_json = os.path.join(cfg.filelists_folder, "errors_asr_vs_texts_v3.json")
    #
    # # recognise_filelist(cfg.amai_path, cfg.all_v3_json, texts_distortion_json, recognition_errors_json)
    # # find_errors(texts_distortion_json, errors_asr_vs_texts_v3_json, exclude_json=exclude_json)
    #
    # # find_errors(texts_distortion_json, errors_asr_vs_texts_v3_json)
    # wavs_asr_vs_texts_v3_folder = os.path.join(cfg.amai_path, "wavs_errors_asr_vs_texts_v3")
    # # wavs_in_one_folder(errors_asr_vs_texts_v3_json, cfg.amai_path, wavs_asr_vs_texts_v3_folder)
    #
    # confirmed_errors_json = os.path.join(cfg.filelists_folder, "confirmed_errors.json")
    # # corrected_confirmed_errors_json = os.path.join(cfg.filelists_folder, "corrected_confirmed_errors.json")
    # all_v3_asr_corrected_json = os.path.join(cfg.filelists_folder, "all_v3_asr_corrected.json")
    #
    # # confirmed_errors_wavs_folder = os.path.join(cfg.amai_path, "confirmed_errors_wavs")
    # # wavs_in_one_folder(confirmed_errors_json, cfg.amai_path, confirmed_errors_wavs_folder)
    #
    # # correct_confirmed_errors_in_filelist(confirmed_errors_json, corrected_confirmed_errors_json)
    # # merge_filelists_jsons_to_json([cfg.all_v3_json, corrected_confirmed_errors_json], all_v3_asr_corrected_json)
    # all_v4_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_long.json")
    # chopped_json = os.path.join(cfg.filelists_folder, "chopped.json")
    # chopped_distiortions = os.path.join(cfg.filelists_folder, "chopped_distortions.json")
    # errors_asr_vs_texts_chopped_json = os.path.join(cfg.filelists_folder, "errors_asr_vs_texts_chopped.json")
    #
    # wavs_asr_vs_texts_chopped_folder = os.path.join(cfg.amai_path, "wavs_errors_asr_vs_texts_chopped")
    # # recognise_filelist(cfg.amai_path, chopped_json, chopped_distiortions, recognition_errors_json)
    # # merge_filelists_jsons_to_json([texts_distortion_json, chopped_distiortions], texts_distortion_json)
    # # find_errors(chopped_distiortions, errors_asr_vs_texts_chopped_json)
    # # wavs_in_one_folder(errors_asr_vs_texts_chopped_json, cfg.amai_path, wavs_asr_vs_texts_chopped_folder, rename=False)
    # confirmed_errors_json = os.path.join(cfg.filelists_folder, "chopped_corrected_confirmed_errors.json")
    all_v4_with_chopped_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped.json")
    chopped_corrected_confirmed_errors_json = os.path.join(cfg.filelists_folder, "chopped_corrected_confirmed_errors.json")
    all_v4_with_chopped_asr_checked_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked.json")
    merge_filelists_jsons_to_json([all_v4_with_chopped_json, chopped_corrected_confirmed_errors_json],
                                  all_v4_with_chopped_asr_checked_json)
    pass


if __name__ == '__main__':
    main()