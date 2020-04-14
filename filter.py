import os
import soundfile

import config as cfg
from utils import load_json, dump_json


def get_wavs_duration(wavs_path, out_json):
    wavs_duration = {}
    for i, filename in enumerate(os.listdir(wavs_path)):
        if filename.split(".")[-1] == "wav":
            audio, sample_rate = soundfile.read(os.path.join(wavs_path, filename))
            wavs_duration[filename] = audio.shape[0] / sample_rate
            print("\rProccesed %d audios" % i, end="")

    dump_json(wavs_duration, out_json)
    print()
    
    return wavs_duration


def filter_filelist(filelist_json, wavs_duration, filtered_filelist_json):
    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration)

    filtered_wavename_to_text = {}
    short_cnt = 0
    long_cnt = 0

    for wavname in wavname_to_text:
        if cfg.min_duration < wavs_duration[wavname] < cfg.max_duration and len(wavname_to_text[wavname]) > cfg.min_len:
            filtered_wavename_to_text[wavname] = wavname_to_text[wavname]
        if wavs_duration[wavname] < cfg.min_duration or len(wavname_to_text[wavname]) < cfg.min_len:
            short_cnt += 1
        if wavs_duration[wavname] > cfg.max_duration:
            long_cnt += 1

    dump_json(filtered_wavename_to_text, filtered_filelist_json)

    print("Input: {} audios\nOutput: {} audios\nRemoved:\n    short: {}\n    long: {}\n    total: {}"
          .format(len(wavname_to_text), len(filtered_wavename_to_text), short_cnt, long_cnt, short_cnt + long_cnt))


def main():
    wavs_duration_json = os.path.join(cfg.ruslan_path, "wavs_duration.json")
    filter_filelist(cfg.all_streesed_v4_json, wavs_duration_json, cfg.all_streesed_filtered_v4_json)
    pass


if __name__ == "__main__":
    main()
