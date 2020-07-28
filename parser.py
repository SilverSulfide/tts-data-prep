import xml.etree.ElementTree as ET
from collections import defaultdict
import math

root = ET.parse('filelist/files.xml').getroot()


def find_test_set(datasize, num_speakers, duration_per_speaker, frac=0.1, req_dur=3):
    # set max amount of speakers to 10%
    speaker_lim = math.floor(frac * num_speakers)
    # construct zipped list
    duration_per_speaker = [(key, duration_per_speaker[key]) for key in duration_per_speaker]
    duration_per_speaker = sorted(duration_per_speaker, key=lambda x: x[1])

    # slide amount of speakers over duration array
    start = 0
    end = speaker_lim
    test_len = sum([float(x[1]) for x in duration_per_speaker[start:end]])
    while test_len / 60 / 60 < req_dur:
        start = start + speaker_lim
        end = end + speaker_lim
        test_len = sum([float(x[1]) for x in duration_per_speaker[start:end]])
    test_set = [int(x[0]) for x in duration_per_speaker[start:end]]
    print("Unique test speakers: ", len(list(set(test_set))), " Required test speakers: ", speaker_lim)
    print("Length of test set: ", test_len / 60 / 60, "h")
    return test_set, test_len


def checker(lens, names, frac):
    total_len = sum(lens)
    checksum = lens[0]
    index = 1
    while checksum / total_len < frac:
        checksum = checksum + lens[index]
        index = index + 1
    index = index - 1
    train_files = names[:index]
    val_files = names[index:]

    return train_files, val_files


def find_train_val(all_data, test_set, frac=0.9):
    train_files = []
    val_files = []
    counter = 0
    for speaker in all_data:
        if int(speaker) not in test_set:
            lens = [x[1] for x in all_data[speaker]]
            names = [x[0] for x in all_data[speaker]]

            temp_train, temp_val = checker(lens, names, frac)
            train_files.extend(temp_train)
            val_files.extend(temp_val)
            counter = counter + 1

    print("Train/val has", counter, "unique speakers")
    return train_files, val_files


def cleaner(line):
    # recursively remove () brackets
    l_bracket = line.find("(")

    while l_bracket != -1:
        r_bracket = line.find(")")
        line = line.replace(line[l_bracket:r_bracket + 1], "")
        l_bracket = line.find("(")

    # recursively remove [] brackets
    l_bracket = line.find("[")

    while l_bracket != -1:
        r_bracket = line.find("]")
        line = line.replace(line[l_bracket:r_bracket + 1], "")
        l_bracket = line.find("[")

    # recursively remove <> brackets
    l_bracket = line.find("<")
    while l_bracket != -1:
        r_bracket = line.find(">")
        line = line.replace(line[l_bracket:r_bracket + 1], "")
        l_bracket = line.find("<")

    # recursively remove {} brackets
    l_bracket = line.find("{")
    while l_bracket != -1:
        r_bracket = line.find("}")
        line = line.replace(line[l_bracket:r_bracket + 1], "")
        l_bracket = line.find("{")

    # recursively remove @
    l_bracket = line.find("@")
    while l_bracket != -1:
        line = line.replace("@", "")
        l_bracket = line.find("@")

    line = line.strip()

    return line


uncut = 0
cut = 0

# Extract useful information
files_per_speaker = defaultdict(int)
duration_per_speaker = defaultdict(float)
all_data = defaultdict(list)

hist = []
for file in root.findall("file"):
    value = file.get("name")
    print(value)
    for fragment in file.findall("fragment"):

        ids = fragment.get("speaker")
        for part in fragment.findall("part"):
            name = part.attrib['audio_file']
            dur = part.attrib['length']
            uncut = uncut + float(dur)
            txt = cleaner(part.text)
            # This is the main workflow
            if txt != "":
                cut = cut + float(dur)
                hist.append(len(txt))
                files_per_speaker[ids] = files_per_speaker[ids] + 1
                duration_per_speaker[ids] = duration_per_speaker[ids] + float(dur)
                all_data[ids].append((name, float(dur)))
            # else:
            # print("Removed: ", part.text)
print(files_per_speaker)
print(duration_per_speaker)
print(all_data)
test_set, test_len = find_test_set(cut, len(duration_per_speaker), duration_per_speaker)
print("Initial duration:", uncut, "sec")
print("Cut duration:", cut, "sec")
hist = sorted(hist)[::-1]
print("Max file: ", max(hist), "chars")
print(hist[:100])

# print("Fraction of test set: ", test_len / cut)
#
# train_set, val_set = find_train_val(all_data, test_set)
#
# print("All sets generated...")
# print("Writing data...")
#
# path = "/home/TILDE.LV/martins.kuznecovs/asr/16000/"
# val_speakers = []
# train_speakers = []
# test_speakers = []
# val_dur = 0
# train_dur = 0
# test_dur = 0
# with open("filelist/train_list.txt", 'w', encoding='utf-8') as out_f:
#     with open("filelist/val_list.txt", 'w', encoding='utf-8') as val_f:
#         with open("filelist/test_list.txt", 'w', encoding='utf-8') as test_f:
#             for file in root.findall("file"):
#                 value = file.get("name")
#                 for fragment in file.findall("fragment"):
#
#                     ids = fragment.get("speaker")
#                     for part in fragment.findall("part"):
#                         name = part.attrib['audio_file']
#                         dur = part.attrib['length']
#                         txt = cleaner(part.text)
#                         if txt != "":
#                             if int(ids) in test_set:
#                                 test_f.write(path + name + "|" + txt + "\n")
#                                 test_set.append(int(ids))
#                                 test_dur = test_dur + float(dur)
#                             else:
#                                 if name in train_set:
#                                     out_f.write(path + name + "|" + txt + "\n")
#                                     train_speakers.append(int(ids))
#                                     train_dur = train_dur + float(dur)
#                                 else:
#                                     val_f.write(path + name + "|" + txt + "\n")
#                                     val_speakers.append(int(ids))
#                                     val_dur = val_dur + float(dur)
#
# val_speakers = list(set(val_speakers))
# train_speakers = list(set(train_speakers))
# test_speakers = list(set(test_speakers))
#
# try:
#     assert (sorted(val_speakers) == sorted(train_speakers))
# except AssertionError:
#     print(len(val_speakers) - len(train_speakers), "speakers from validation set do not exist in train set")
# assert (x not in val_speakers for x in test_speakers)
# assert (x not in train_speakers for x in test_speakers)
# print()
# print("All checks passed!")
# print("-----------------")
# print("Test%: ", test_dur / cut * 100, " = ", test_dur / 60 / 60, "h")
# print("Val%: ", val_dur / cut * 100, " = ", val_dur / 60 / 60, "h")
# print("Train%: ", train_dur / cut * 100, " = ", train_dur / 60 / 60, "h")
