import os

import config as cfg
from utils import load_json, dump_json


def check_stress_placement(stress_json, mistakes_json, mistakes_filelist_json):
    d = load_json(stress_json) 

    mistakes = []
    ids_of_mistakes = []
    cnt_bad_mistakes = 0
    for item in d:
        text = item["text"]
        text = text.replace("\"", " ")
        text = text.replace(":", " ")
        text = text.replace(".", " ")
        text = text.replace(".", " ")
        text = text.replace("!", " ")
        text = text.replace("?", " ")
        text = text.replace(",", " ")
        text = text.replace("–", " ")
        text = text.replace("‑", " ")
        text = text.replace("-", " ")
        words = text.split()

        mistake_found = False
        bad_mistake_found = False
        item["errors"] = []
        item
        for word in words:
            vowels_count = sum(map(word.lower().count, u"уеыаоэяиюё"))
            if word.count("+") > 1 or (word.count("+") < 1 and vowels_count > 1)\
               and word != "таки" and word != "нибудь" and word != "либо":
                item["errors"].append(word)
                mistake_found = True
                if word[0].lower() == word[0]:
                    bad_mistake_found = True

        if mistake_found:
            mistakes.append(item)
            ids_of_mistakes.append(item["text_id"])
        if bad_mistake_found:
            cnt_bad_mistakes += 1

    if len(mistakes) > 0:
        dump_json(mistakes, mistakes_json)
        dump_json(ids_of_mistakes, mistakes_filelist_json)

    print("{} mistakes out of {} entries. At least {} of them are not names"\
           .format(len(mistakes), len(d), cnt_bad_mistakes))


def emphas_list_to_dict(list_json, out_dict_json):
    info_list = load_json(list_json)
    info_dict = {}

    for item in info_list:
        info_dict[item["text_id"]] = item["text"]

    dump_json(info_dict, out_dict_json)


# first dictionary -- lowest priorty, last -- maximum priority
def render_corrections(jsons_list, out_json):
    lists = []
    for path_json in jsons_list:
        lists.append(load_json(path_json))

    rendered = {}
    for d in lists:
        for item in d:
            rendered[item["text_id"]] = item["text"]

    result = []
    for text_id in rendered:
        result.append({"text_id" : text_id, "text" : rendered[text_id]})

    dump_json(result, out_json)


def main():

    pass


if __name__ == '__main__':
    main()