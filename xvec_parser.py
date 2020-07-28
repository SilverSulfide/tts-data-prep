import numpy as np

with open("xvecs/output_64.txt", 'r', encoding='utf-8') as out_f:
    lines = out_f.readlines()
    for line in lines:
        line = line.split("  ")
        name = line[0]
        vec = line[1].split(" ")
        vec = vec[1:-1]
        vec = list(map(float, vec))
        print(len(vec))
        vec = np.array(vec)
        name = name.split("-")[1]
        print(name)
        name = name.replace(".wav", "")
        np.save("output_64/" + name + ".npy", vec)
