import os
import glob
import soundfile

from utils import add_suffix, dump_json


def correct_txt_filelist(filelist_txt, out_folder):
    filelist = open(filelist_txt).read().split("|-1")
    corrected_filelist = []
    for line in filelist:
        if line != "\n":
            wavname, text = line.split("|")
            corrected_filelist.append((wavname + "|" + text).replace("\n", ""))

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    corrected_filelist_txt = os.path.join(out_folder, add_suffix(filelist_txt, "corrected"))
    open(corrected_filelist_txt, "w+").write("\n".join(corrected_filelist))

    return corrected_filelist_txt


def correct_multiple_txt_filelists(target_filelists_folder, out_folder):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for filelist_txt in glob.glob(target_filelists_folder):
        correct_txt_filelist(filelist_txt, out_folder)


def main():
    pass


if __name__ == '__main__':
    main()