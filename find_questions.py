import os
from random import shuffle
import numpy as np

import config as cfg
from utils import load_json, dump_json, filelist_json_to_txt, train_val_split_json_to_txt


def sample_questions_non_questions_filelist(filelist_json, out_json):
	wavname_to_text = load_json(filelist_json)

	questions = []
	non_questions = []
	for wavname in wavname_to_text:
		if "?" in wavname_to_text[wavname]:
			questions.append(wavname)
		else:
			non_questions.append(wavname)

	non_questions_samples = list(np.random.choice(non_questions, len(questions), replace=False))
	mixed_samples = questions + non_questions_samples
	shuffle(mixed_samples)

	result = {}
	for wavname in mixed_samples:
		result[wavname] = wavname_to_text[wavname]
	print("%d audios out of %d are in questions-non-questions dataset" % (len(result), len(wavname_to_text)))

	dump_json(result, out_json)


def main():
	questions_non_questions_json = os.path.join(cfg.ruslan_path, "questions_non_questions_all.json")
	sample_questions_non_questions_filelist(cfg.all_streesed_filtered_v4_json,
											questions_non_questions_json)
	questions_non_questions_folder = os.path.join(cfg.ruslan_path, "questions_non_questions_stressed")

	train_val_split_json_to_txt(questions_non_questions_json, questions_non_questions_folder)



if __name__ == "__main__":
    main()
