import re, seaborn as sns
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import ListedColormap

import csv

x, y, z, color = [], [], [], []
ignore_first = True
with open('./Bureau/benchmark_ai_chatbot_cs/azure/results.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        if ignore_first:
            ignore_first = False
            continue
        x.append(float(row[1]))
        y.append(float(row[2]))
        z.append(float(row[3]))

        color.append(int(row[4]))

fig = plt.figure(figsize=(8,8))
ax = Axes3D(fig, auto_add_to_figure=False)
fig.add_axes(ax)
cmap = sns.color_palette("coolwarm", as_cmap=True).reversed()
sc = ax.scatter(x, y, z, s=40, c=color, marker='o', cmap=cmap, alpha=1)
ax.set_xlabel('Embeddings')
ax.set_ylabel('Similarity')
ax.set_zlabel('Uncertainty')
plt.legend(*sc.legend_elements(), bbox_to_anchor=(1.05, 1), loc=2)


if True:
    def animate(i):
        ax.view_init(elev=30, azim=i)
        return fig,

    anim = animation.FuncAnimation(fig, animate, frames=360, interval=20, blit=False)
    anim.save('basic_animation.gif', fps=30)

