import string
from collections import defaultdict
from pydub import AudioSegment

remove = string.punctuation
remove = remove.replace(".", "")
remove = remove.replace("!", "")
remove = remove.replace("?", "")
remove = remove.replace(";", "")

filename = "sandra_data/filelists/ctm.new.edited"
punct_file = "sandra_data/filelists/text_final"

path = "C:/Users/martins.kuznecovs/Documents/data/sandra_new/wav/"
out_path = "out_data/"


def checker(punct, word, prev_word, name):
    text = punct[name]

    for n, token in enumerate(text):
        if token == word and n > 1:
            if text[n - 2] == prev_word:
                if text[n - 1] in ".?!;":
                    print(name, ":", prev_word, text[n - 1], word)
                    return True

    return False


def checker2(punct, word, prev_word, name):
    if prev_word[-1] in "!.?;":
        return True
    return False


def find_pauses(ctm_file, punct_file, threshold=0.25, check=checker2):
    # parse lines
    lines = []
    with open(ctm_file, encoding='utf-8') as f:
        original = f.readlines()
        for line in original:
            line = line.split(" ")
            # get rid of newline
            lines.append(line[:-1])

    punct = {}
    with open(punct_file, encoding='utf-8') as f:
        punctuation_lines = f.readlines()
        for line in punctuation_lines:
            name = line.strip().split(" ")[0]
            current_text = line.strip().split(" ")[1:]
            current_text = [i for i in current_text if i not in remove]
            current_text = [i for i in current_text if i != " "]
            current_text = [i for i in current_text if i != ".."]
            current_text = [i for i in current_text if i != "..."]
            punct[name] = current_text

    ids = []
    file = ""
    transcription = {}
    words = []

    for n, line in enumerate(lines):
        temp_file = line[0]
        if file != temp_file:
            file = temp_file
            words = [line[4]]
        else:
            words.append(line[4])
            transcription[temp_file] = words
            pause = float(line[2]) - (float(lines[n - 1][2]) + float(lines[n - 1][3]))
            if pause > threshold:
                if check(punct, line[4], lines[n - 1][4], temp_file):
                    ids.append(
                        (temp_file, lines[n - 1][4], line[4], pause, float(lines[n - 1][2]) + float(lines[n - 1][3]),
                         float(line[2])))

    return ids, transcription, threshold


ids, trsc, threshold = find_pauses(filename, punct_file)

print("Using: ", filename)
print("Thershold: ", threshold, "s")
print("Pauses found: ", len(ids))

# construct pauses based on file name
pauses = defaultdict(list)
for pause in ids:
    name = pause[0]
    pauses[name].append(pause[1:])

print(pauses)

with open(out_path + "file_list.txt", "w", encoding='utf-8') as out_txt:
    for key in pauses:
        # print(key)
        current_file = pauses[key]
        # print(current_file)
        cutter = []
        text_splits = []
        # loop through each pause construct cutter
        previous_len = 0
        for n, pause in enumerate(current_file):
            t1 = pause[3] * 1000 - previous_len
            t2 = pause[4] * 1000 - previous_len
            buffer = (t2 - t1) / 2
            previous_len = previous_len + t2 - buffer
            cut = (t1 + buffer)
            cutter.append(cut)
            text_splits.append((pause[0], pause[1]))

        # print(cutter)
        # construct correct text segments
        segment_text = []
        text = " ".join(trsc[key])
        for split in text_splits:
            w1, w2 = split
            w = w1 + " " + w2
            ids = text.find(w)
            assert (ids != -1)
            segment_text.append(text[:ids + len(w1)])
            text = text[ids + len(w1):]

        # handle last segment
        segment_text.append(text)
        # print(segment_text)
        # perform sequential cutting
        with open(path + key + ".wav", 'rb') as in_f:
            current_audio = AudioSegment.from_wav(in_f)

        for n, split in enumerate(cutter):
            part1 = current_audio[:split]
            with open(out_path + key + "_cut_" + str(n) + ".wav", 'wb') as out_sound:
                handle = part1.export(out_sound, format="wav")
            handle.close()
            out_txt.write(key + "_cut_" + str(n) + ".wav" + "|" + segment_text[n] + "\n")
            current_audio = current_audio[split:]

        # handle last cut
        out_txt.write(key + "_cut_" + str(n + 1) + ".wav" + "|" + segment_text[n + 1] + "\n")
        with open(out_path + key + "_cut_" + str(n + 1) + ".wav", 'wb') as out_sound:
            handle = current_audio.export(out_sound, format="wav")
        handle.close()

# open existing file list and replace uncut segments with cut
with open("sandra_data/new/train_filelist.txt", encoding='utf-8') as in_f:
    original_lines = in_f.readlines()

server_path = "/home/TILDE.LV/martins.kuznecovs/cut_sandra/"
line_dict = defaultdict(list)
with open("out_data/file_list.txt", encoding='utf-8') as in_f:
    lines = in_f.readlines()
    for line in lines:
        name = line.split("|")[0]
        name = name[:-10]
        line_dict[name].append(server_path + line)

andris_path = "/home/TILDE.LV/andris.varavs/sandra_tts/wav/"
n = 0
with open("out_data/train_filelist.txt", 'w', encoding='utf-8') as out_f:
    for line in original_lines:
        name = line.split("|")[0]
        name = name.replace("/home/TILDE.LV/andris.varavs/sandra_tts/wav/", "")
        name = name.replace(".wav", "")
        if name in line_dict:
            n = n + 1
            print("writing: ", name)
            for new_line in line_dict[name]:
                out_f.write(new_line)
        else:
            out_f.write(line)

assert (n == len(line_dict))