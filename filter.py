import os
import soundfile

import config as cfg
from utils import load_json, dump_json, get_wavs_duration, count_filelist_duration


def filter_filelist(filelist_json, wavs_duration, filtered_filelist_json=None, print_long_wavnames=False):
    print("\n" + "=" * 10 + " Removing too long and too short wavnames from filelist " + "=" * 10)

    wavname_to_text = load_json(filelist_json)
    wavs_duration = load_json(wavs_duration)

    filtered_wavename_to_text = {}
    short_cnt = 0
    long_cnt = 0

    approved_duration = 0
    removed_duration = 0
    short_duration = 0
    long_duration = 0

    for wavname in wavname_to_text:
        try:
            if cfg.min_duration < wavs_duration[wavname] < cfg.max_duration\
                    and len(wavname_to_text[wavname]) > cfg.min_len:
                filtered_wavename_to_text[wavname] = wavname_to_text[wavname]
                approved_duration += wavs_duration[wavname]
            else:
                removed_duration += wavs_duration[wavname]

            if wavs_duration[wavname] < cfg.min_duration or len(wavname_to_text[wavname]) < cfg.min_len:
                short_cnt += 1
                short_duration += wavs_duration[wavname]

            if wavs_duration[wavname] > cfg.max_duration:
                long_cnt += 1
                long_duration += wavs_duration[wavname]
                if print_long_wavnames:
                    print("Removed:", wavname, "duration: %.2f" % wavs_duration[wavname])
                    print(wavname_to_text[wavname])
        except:
            print("\n missing wav:" + wavname + "\n")

    if filtered_filelist_json is not None:
        dump_json(filtered_wavename_to_text, filtered_filelist_json)

    short_duration /= 60 * 60
    long_duration /= 60 * 60
    removed_duration /= 60 * 60
    approved_duration /= 60 * 60

    print("\nInput: %d audios, total duration: %.2f" % (len(wavname_to_text), approved_duration + removed_duration))
    print("Output: %d audios, total duration %.2f" % (len(filtered_wavename_to_text), approved_duration))
    print("Removed: ")

    print("        short:")
    print("              %d audios" % short_cnt)
    print("              %.2f hours" % short_duration)

    print("        long:")
    print("              %d audios" % long_cnt)
    print("              %.2f hours" % long_duration)

    print("        total:")
    print("              %d audios" % (long_cnt + short_cnt))
    print("              %.2f hours" % removed_duration)


def main():
    # # all_v3_asr_corrected_json = os.path.join(cfg.filelists_folder, "all_v3_asr_corrected.json")
    # wavs_duration_json = os.path.join(cfg.filelists_folder, "wavs_duration.json")
    # # get_wavs_duration(cfg.amai_path, wavs_duration_json)
    # chopped_json = os.path.join(cfg.filelists_folder, "chopped.json")
    # filter_filelist(chopped_json, wavs_duration_json, print_long_wavnames=True)
    # # result_json = os.path.join(cfg.filelists_folder, "all_v3_asr_corrected_filtered.json")
    # all_v4_with_chopped_asr_checked = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked.json")
    # all_v4_with_chopped_asr_checked_filtered = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")
    all_v4_with_chopped_asr_checked_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked.json")
    all_v4_with_chopped_asr_checked_filtered_json = os.path.join(cfg.filelists_folder, "all_v4_with_chopped_asr_checked_filtered.json")

    filter_filelist(all_v4_with_chopped_asr_checked_json,
                    cfg.wavs_duration_json,
                    all_v4_with_chopped_asr_checked_filtered_json,
                    print_long_wavnames=True)

    count_filelist_duration(cfg.all_v3_json, cfg.wavs_duration_json)
    count_filelist_duration(all_v4_with_chopped_asr_checked_json, cfg.wavs_duration_json)
    count_filelist_duration(all_v4_with_chopped_asr_checked_filtered_json, cfg.wavs_duration_json)

    pass


if __name__ == "__main__":
    main()
