import string
import re
split = "~"
real = {}
remove = string.punctuation
pattern = r"[{}]".format(remove)

with open("gold_text/newsegs", encoding="utf-8") as f:
    real_lines = f.readlines()
f.close()
with open("sandra_data/filelists/text.csv", encoding='utf-8') as f:
    original = f.readlines()
    assert (len(original) == len(real_lines))
    for n, line in enumerate(original):
        name = line.strip().split(split)[0]
        text = line.strip().split(split)[1]
        temp = real_lines[n]
        #temp = re.sub(pattern, "", temp)
        real[name] = temp

with open("sandra_data/filelists/text_old", encoding='utf-8') as in_f:
    with open("sandra_data/filelists/text_final", 'w', encoding='utf-8') as out_f:
        lines = in_f.readlines()
        for line in lines:
            line = line.split(" ", 1)
            name = line[0]
            out_f.write(name + " " + real[name])
