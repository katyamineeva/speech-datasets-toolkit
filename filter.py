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


def filter_filelist(filelist_json,
                    wavs_duration,
                    out_json=None,
                    min_duration=cfg.min_duration,
                    max_duration=cfg.max_duration,
                    min_len=cfg.min_len):
    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration)

    filtered_wavename_to_text = {}
    short_cnt = 0
    long_cnt = 0

    for wavname in wavname_to_text:
        if min_duration < wavs_duration[wavname] < max_duration and len(wavname_to_text[wavname]) > min_len:
            filtered_wavename_to_text[wavname] = wavname_to_text[wavname]
        if wavs_duration[wavname] < min_duration or len(wavname_to_text[wavname]) < min_len:
            short_cnt += 1
        if wavs_duration[wavname] > max_duration:
            long_cnt += 1

    if out_json is not None:
        dump_json(filtered_wavename_to_text, out_json)

    print("Input: {} audios\nOutput: {} audios\nRemoved:\n    short: {}\n    long: {}\n    total: {}"
          .format(len(wavname_to_text), len(filtered_wavename_to_text), short_cnt, long_cnt, short_cnt + long_cnt))

    return filtered_wavename_to_text
