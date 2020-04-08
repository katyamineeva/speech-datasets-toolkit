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


def main():
    
    pass


if __name__ == "__main__":
    main()