import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

import csv
import tqdm

PATH_CSV = 'azure/results_gpt_judge/results_mistral_ignos_rde.csv'

x, y, z, color = [], [], [], []
ignore_first = True
with open(PATH_CSV) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in tqdm.tqdm(spamreader):
        if ignore_first:
            ignore_first = False
            continue
        x.append(float(row[1]))
        y.append(float(row[2]))
        z.append(float(row[3]))

        color_id = row[4]
        try:
            color_id = int(color_id)
        except:
            color_id = float(color_id)
        if color_id == 0:
            color.append("red")
        elif color_id == 0.5:
            color.append("green")
        elif color_id == 1:
            color.append("blue")
        elif color_id == 2:
            color.append("purple")
        else:
            print("Error on row", row)

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

