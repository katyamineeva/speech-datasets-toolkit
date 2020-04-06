import os
import json

from utils import load_json

def get_amai_features(filelist_json):
    wavname_to_text = load_json(filelist_json)
    texts_total = len(wavname_to_text)

    # depenent_sentence_signs = [", что",
    #                            ", чего",
    #                            ", чьего",
    #                            ", чем"
    #                            ", которой",
    #                            ", который",
    #                            ", которым",
    #                            ", которыми",
    #                            ", как",
    #                            ", кем",
    #                            ", кто",
    #                            ", кого",
    #                            ", какой",
    #                            ", какая",
    #                            ", каким"
    #                            ]

    commas_cnt = 0
    depenent_sentences_lower_bound = 0
    questions_cnt = 0
    exclamations_cnt = 0
    colons_cnt = 0
    semicolons_cnt = 0
    dashes_cnt = 0


    for wavname in wavname_to_text:
        text = wavname_to_text[wavname]
        if "," in text:
            commas_cnt += 1

        if "?" in text:
            questions_cnt += 1

        if "!" in text:
            exclamations_cnt += 1

        if ":" in text:
            colons_cnt += 1

        if ";" in text:
            semicolons_cnt += 1

        if "-" in text:
            dashes_cnt += 1

    print("%2f sentences contain at least one comma" % (commas_cnt / texts_total))
    print("%2f sentences are questions" % (questions_cnt / texts_total))
    print("%2f sentences are exclamations" % (exclamations_cnt / texts_total))
    print("%2f sentences contains a colon" % (colons_cnt / texts_total))
    print("%2f sentences contains a semicolon" % (semicolons_cnt / texts_total))
    print("%2f sentences contains a dashes" % (exclamations_cnt / texts_total))


def main():
    pass


if __name__ == "__main__":
    main()
