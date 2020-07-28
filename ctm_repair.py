import string

ctm_file = "sandra_data/filelists/ctm.new"
punct_file = "sandra_data/filelists/text_final"
punct = {}
remove = string.punctuation
remove = remove.replace(".", "")
remove = remove.replace("!", "")
remove = remove.replace("?", "")
remove = remove.replace(";", "")
with open(punct_file, encoding='utf-8') as f:
    punctuation_lines = f.readlines()
    for line in punctuation_lines:
        name = line.strip().split(" ")[0]
        current_text = line.strip().split(" ")[1:]
        current_text = [i for i in current_text if i not in remove]
        current_text = [i for i in current_text if i != " "]
        current_text = [i for i in current_text if i != ".."]
        current_text = [i for i in current_text if i != "..."]
        # print(current_text)
        temp = []
        for n, token in enumerate(current_text):
            if token not in "?.!;":
                if n < len(current_text) - 1:
                    if current_text[n + 1] in "?.!;":
                        temp.append(token + current_text[n + 1])
                    else:
                        temp.append(token)
                else:
                    temp.append(token)
        # print(temp)
        punct[name] = temp

# parse lines
lines = []
with open(ctm_file, encoding='utf-8') as f:
    original = f.readlines()
    for line in original:
        print(repr(line))
        line = line.split(" ")
        # get rid of newline
        lines.append(line[:-1])

curr_name = ""
n = 0
for line in lines:
    name = line[0]
    if name != curr_name:
        n = 0
        curr_name = name
    word = punct[name][n]
    if line[-1] != word:
        print(line[-1], "->", word)
        line[-1] = word
    n = n + 1

with open("sandra_data/filelists/ctm.new.edited", 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(" ".join(line) + " " + "\n")
