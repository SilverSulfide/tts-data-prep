import xml.etree.ElementTree as ET
from collections import defaultdict


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


def find_train_val(all_data, test_set, frac=0.95):
    train_files = []
    val_files = []
    counter = 0
    for speaker in all_data:
        if speaker not in test_set:
            lens = [x[1] for x in all_data[speaker]]
            names = [x[0] for x in all_data[speaker]]

            temp_train, temp_val = checker(lens, names, frac)
            train_files.extend(temp_train)
            val_files.extend(temp_val)
            counter = counter + 1

    print("Train/val has", counter, "unique speakers")
    return train_files, val_files


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


root = ET.parse('filelist/files.xml').getroot()
uncut = 0
cut = 0

# Extract useful information
files_per_speaker = defaultdict(int)
duration_per_speaker = defaultdict(float)
all_data = defaultdict(list)

hist = []
for file in root.findall("file"):
    value = file.get("name")
    for fragment in file.findall("fragment"):

        ids = str(fragment.get("speaker"))
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

root = ET.parse('filelist/speakers.xml').getroot()
genders = {}
for speaker in root.findall("speaker"):
    name = speaker.get("speaker_id")
    gender = speaker.get("gender")
    if gender == "female":
        genders[name] = 0
    elif gender == "male":
        genders[name] = 1
    else:
        print("yikes.")

num = 125
blacklist = []
total_files = 0
for speaker in files_per_speaker:
    total_files = total_files + files_per_speaker[speaker]
    if files_per_speaker[speaker] < num:
        blacklist.append(speaker)
    elif genders[speaker] == 1:
        blacklist.append(speaker)

dur = 0
unique = 0
total_new = 0
clean_list = []
for speaker in duration_per_speaker:
    if speaker not in blacklist:
        clean_list.append(speaker)
        dur = dur + duration_per_speaker[speaker]
        total_new = total_new + files_per_speaker[speaker]
        unique = unique + 1


male = 0
female = 0
for speaker in clean_list:
    if genders[speaker] == 0:
        female = female + 1
    else:
        male = male + 1

test_set = blacklist

print("Old average per speaker: ", uncut / (unique + len(blacklist)) / 60, "min")
print("Keeping only speakers with at least", num, "files")
print("Duration: ", dur / 60 / 60, "h")
print("Speakers: ", unique)
print("New average per speaker: ", dur / unique / 60, "min")
print("Male:", male)
print("Female:", female)
print("Removed", len(blacklist), "speakers")
print("Removed", (uncut - dur) / 60 / 60, "h")

# perform data split and writing
train_set, val_set = find_train_val(all_data, test_set)

print("All sets generated...")
print("Writing data...")

path = "/home/TILDE.LV/martins.kuznecovs/asr/16000/"
val_speakers = []
train_speakers = []
val_dur = 0
train_dur = 0
cut = dur

root = ET.parse('filelist/files.xml').getroot()
with open("filelist/gender/female/train_list.txt", 'w', encoding='utf-8') as out_f:
    with open("filelist/gender/female/val_list.txt", 'w', encoding='utf-8') as val_f:
        for file in root.findall("file"):
            value = file.get("name")
            for fragment in file.findall("fragment"):

                ids = fragment.get("speaker")
                for part in fragment.findall("part"):
                    name = part.attrib['audio_file']
                    dur = part.attrib['length']
                    txt = cleaner(part.text)
                    if txt != "":
                        if name in train_set:
                            out_f.write(path + name + "|" + txt + "\n")
                            train_speakers.append(int(ids))
                            train_dur = train_dur + float(dur)
                        elif name in val_set:
                            val_f.write(path + name + "|" + txt + "\n")
                            val_speakers.append(int(ids))
                            val_dur = val_dur + float(dur)

val_speakers = list(set(val_speakers))
train_speakers = list(set(train_speakers))

try:
    assert (sorted(val_speakers) == sorted(train_speakers))
except AssertionError:
    print(len(val_speakers) - len(train_speakers), "speakers from validation set do not exist in train set")
assert (int(x) not in val_speakers for x in blacklist)
assert (int(x) not in train_speakers for x in blacklist)
print()
print("All checks passed!")
print("-----------------")
print("Val%: ", val_dur / cut * 100, " = ", val_dur / 60 / 60, "h")
print("Train%: ", train_dur / cut * 100, " = ", train_dur / 60 / 60, "h")