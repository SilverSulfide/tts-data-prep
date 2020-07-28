import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
from tqdm import tqdm

# TODO: add tsne option
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

root = ET.parse('filelist/speakers.xml').getroot()

data = {}

for speaker in root.findall("speaker"):
    name = int(speaker.get("speaker_id"))
    gender = speaker.get("gender")
    if gender == "female":
        data[name] = 0
    elif gender == "male":
        data[name] = 1
    else:
        print("yikes.")

ids = []
big_data = defaultdict(list)

print("Reading vectors...")
with open("xvecs/output_64.txt", 'r', encoding='utf-8') as out_f:
    lines = out_f.readlines()
    for line in tqdm(lines):
        line = line.split("  ")
        name = line[0]
        split = name.index("-")
        idx = int(name[:split])
        name = name.split("-")[1]
        name = name.replace(".wav", ".npy")
        xvec = np.load("output_64/" + name, allow_pickle=True)
        ids.append(idx)
        big_data[idx].append(xvec)

print("Vectors successfully read.")

# select 20 random speakers
amount = 20
files = 20
key = np.random.choice(max(ids), size=amount, replace=False)
# chose only the ones that have 20 points
big = True

if big:
    print("Using minimum", files, "files per speaker")
    key = []
    for speaker in big_data:
        if len(big_data[speaker]) >= files:
            key.append(speaker)
    key = np.random.choice(key, size=amount, replace=False)
X = []
y = []
y_gen = []

for speaker in key:
    n = 0
    for xvec in big_data[speaker]:
        X.append(xvec)
        y.append(speaker)
        y_gen.append(data[speaker])
        n = n + 1
        if n == files:
            break

meme = {}
for n, speaker in enumerate(list(set(y))):
    meme[speaker] = n

X = np.array(X)
# perform PCA
pca = PCA(n_components=2)
X_r = pca.fit(X).transform(X)

print("PCA complete")
plt.subplot(121)

print("Plotting")
colors = []
color_names = ['black', 'darkorange', 'darkgreen', 'lime', 'navy', 'purple', 'magenta', 'red', 'maroon', 'dimgrey',
               'gold',
               'tan', 'olivedrab', 'yellowgreen', 'pink', 'blue', 'cyan', 'royalblue', 'mediumspringgreen', 'peru']
for color in color_names:
    colors.append(mcolors.CSS4_COLORS[color])

colors = np.array(colors)
np.random.shuffle(colors)
colors = colors[:amount]
lw = 2
artists = []
checkmaster = []
labels = []
for i in range(X_r.shape[0]):
    z = plt.scatter(X_r[i, 0], X_r[i, 1], color=colors[meme[y[i]]], alpha=0.8, lw=lw,
                    label=y[i])
    if y[i] not in checkmaster:
        artists.append(z)
        checkmaster.append(y[i])
        labels.append(y[i])

plt.legend(tuple(artists), tuple(labels))
plt.title('PCA based on id, dim=' + str(X.shape[1]))

# Gender stuff
plt.subplot(122)

print("Plotting gender")
colors = []
color_names = ['blue', 'red']
for color in color_names:
    colors.append(mcolors.CSS4_COLORS[color])

name_gender = ["female", "male"]
lw = 2
artists = []
checkmaster = []
labels = []
for i in range(X_r.shape[0]):
    z = plt.scatter(X_r[i, 0], X_r[i, 1], color=colors[y_gen[i]], alpha=0.8, lw=lw,
                    label=name_gender[y_gen[i]])
    if y_gen[i] not in checkmaster:
        artists.append(z)
        checkmaster.append(y_gen[i])
        labels.append(name_gender[y_gen[i]])

plt.legend(tuple(artists), tuple(labels))
plt.title('PCA based on gender, dim=' + str(X.shape[1]))
plt.show()