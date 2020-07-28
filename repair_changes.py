import string

split = "~"

with open("sandra_data/filelists/text_punctuated", encoding='utf-8') as gold:
    with open("sandra_data/filelists/text", encoding='utf-8') as current:
        with open("sandra_data/filelists/what_is", 'w', encoding='utf-8') as is_file:
            gold_lines = gold.readlines()
            current_lines = current.readlines()
            assert (len(gold_lines) == len(current_lines))

            for n, gold_line in enumerate(gold_lines):
                gold_line = gold_line.strip().split(" ")
                name = gold_line[0]
                gold_text = gold_line[1:]
                current_text = current_lines[n].strip().split(" ")[1:]
                if gold_text != current_text:
                    print(gold_text)
                    print(current_text)
                    is_file.write(name + " " + " ".join(current_text) + "\n")
