result = ""
split = "~"
with open("sandra_data/filelists/text.csv", encoding='utf-8') as f:
    original = f.readlines()
    for n, line in enumerate(original):
        name = line.strip().split(split)[0]
        text = line.strip().split(split)[1]
        if n < len(original) - 1:
            result = result + text + "|"
        else:
            result = result + text

with open("sandra_data/filelists/segments.txt", 'w', encoding='utf-8') as f:
    f.write(result)
