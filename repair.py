with open("xvecs/xvector.scp", 'w', encoding='utf-8') as out_f:
    for i in range(1, 17):
        print(i)
        with open("xvecs/xvector." + str(i) + ".scp", 'r', encoding='utf-8') as in_f:
            lines = in_f.readlines()
            for line in lines:
                out_f.write(line)
