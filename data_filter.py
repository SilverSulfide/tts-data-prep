import librosa

filename = "C:/Users/martins.kuznecovs/Documents/data/sandra_new/filelists/train_filelist.txt"
split = "|"
with open(filename, encoding='utf-8') as f:
    original = f.readlines()
    files = [line.strip().split(split)[0] for line in original]

uncut_duration = 0
cut_duration = 0

to_remove = []

for n, file in enumerate(files):
    file = file.replace("/home/TILDE.LV/andris.varavs/sandra_tts/", "C:/Users/martins.kuznecovs/Documents/data/sandra_new/")
    durr = librosa.get_duration(filename=file)
    uncut_duration = uncut_duration + durr

    if durr < 15.0:
        to_remove.append(n)
    else:
        cut_duration = cut_duration + durr

print("Uncut: ", uncut_duration / 60)
print("Cut: ", cut_duration / 60)
print(len(to_remove))
with open("gold_text/train_filelist_15s.txt", 'w',  encoding='utf-8') as f:
    for n, line in enumerate(original):
        if n not in to_remove:
            f.write(line)


uncut_duration = 0

