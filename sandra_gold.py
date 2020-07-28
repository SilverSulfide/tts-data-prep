import docx2txt

text = docx2txt.process("gold_text/SAVSBIZNESS.docx")

text = text.strip()

text = text.replace("izmantojot mentoringu.",
                    "izmantojot mentoringu. Mentorings: uz ilglaicīgu, brīvprātīgu atbalstu bāzētas sistemātiski veidotas attiecības starp veiksmīgu uzņēmēju, kurš dalās savā pieredzē, zināšanās un uzskatos, un otru uzņēmēju, kurš ir gatavs un vēlas gūt pieredzi no šīs apmaiņas. ")

text = text.replace("\n", " ")
text = text.replace("  ", " ")
print(text)

with open("gold_text/gold.txt", "w", encoding='utf-8') as out_f:
    out_f.write(text)
