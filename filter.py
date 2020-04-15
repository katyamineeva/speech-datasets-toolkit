import os
import soundfile

import config as cfg
from utils import load_json, dump_json


def get_wavs_duration(dataset_path, out_json, start_from_scratch=False):
    if os.path.exists(out_json):
        wavs_duration = load_json(out_json)
    else:
        wavs_duration = {}

    for foldername in os.listdir(os.path.join(dataset_path, "dataset")):
        for filename in os.listdir(os.path.join(dataset_path, "dataset", foldername, "wavs")):
            if filename.split(".")[-1] == "wav":
                wavname_original = os.path.join("dataset", foldername, "wavs", filename)
                if wavname_original not in wavs_duration:
                    wavpath = os.path.join(dataset_path, "dataset", foldername, "wavs", filename)

                    audio, sample_rate = soundfile.read(wavpath)
                    wavs_duration[wavname_original] = audio.shape[0] / sample_rate

    dump_json(wavs_duration, out_json)

    return wavs_duration


def filter_filelist(filelist_json, wavs_duration, filtered_filelist_json=None, print_long_wavnames=False):
    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration)

    filtered_wavename_to_text = {}
    short_cnt = 0
    long_cnt = 0

    for wavname in wavname_to_text:
        try:
            if cfg.min_duration < wavs_duration[wavname] < cfg.max_duration\
                    and len(wavname_to_text[wavname]) > cfg.min_len:
                filtered_wavename_to_text[wavname] = wavname_to_text[wavname]
            if wavs_duration[wavname] < cfg.min_duration or len(wavname_to_text[wavname]) < cfg.min_len:
                short_cnt += 1
            if wavs_duration[wavname] > cfg.max_duration:
                long_cnt += 1
                if print_long_wavnames:
                    print("long wav:", wavname)
        except:
            print("\n missing wav:" + wavname + "\n")

    if filtered_filelist_json is not None:
        dump_json(filtered_wavename_to_text, filtered_filelist_json)

    print("\nInput: {} audios\nOutput: {} audios\nRemoved:\n    short: {}\n    long: {}\n    total: {}"
          .format(len(wavname_to_text), len(filtered_wavename_to_text), short_cnt, long_cnt, short_cnt + long_cnt))


def main():
    # all_v3_asr_corrected_json = os.path.join(cfg.filelists_folder, "all_v3_asr_corrected.json")
    wavs_duration_json = os.path.join(cfg.filelists_folder, "wavs_duration.json")
    # get_wavs_duration(cfg.amai_path, wavs_duration_json)
    chopped_json = os.path.join(cfg.filelists_folder, "chopped.json")
    filter_filelist(chopped_json, wavs_duration_json, print_long_wavnames=True)
    # result_json = os.path.join(cfg.filelists_folder, "all_v3_asr_corrected_filtered.json")
    pass


if __name__ == "__main__":
    main()
