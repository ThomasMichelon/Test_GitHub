#!/usr/bin/env python3.8

import matplotlib
import matplotlib.pyplot as plt
import os

# Read ypos
filename='postProcessing/forcesBins/0/forces_bins.dat'
with open(filename, 'r') as f:
    line = f.readlines()[5].replace("(", "").replace(")", "").split()

ypos=[float(i) for i in line[4:]]
ypos=[i-min(ypos) for i in ypos]

# Read F
with open(filename, 'r') as f:
    line = f.readlines()[-1].replace("(", "").replace(")", "").split()

F=[]
for i in range(0,len(ypos)*18,18):
    F.append(float(line[i+1])+float(line[i+4]))

F2=[-f for f in F]

# Plot
fig = matplotlib.pyplot.figure(figsize=(4, 4), dpi=240)
ax=fig.add_axes([0.15,0.15,0.75,0.75])

bordercolor='#6F7582'
ax.spines['bottom'].set_color(bordercolor)
ax.spines['top'].set_color(bordercolor) 
ax.spines['right'].set_color(bordercolor)
ax.spines['left'].set_color(bordercolor)
ax.tick_params(axis='x', colors=bordercolor)
ax.tick_params(axis='y', colors=bordercolor)
ax.yaxis.label.set_color(bordercolor)
ax.xaxis.label.set_color(bordercolor)

background= plt.imread('fig/binsbackground.png')
os.remove('fig/binsbackground.png')
height, width = background.shape[:2]
ar=height/width
plt.imshow(background,aspect='auto', extent=[min(ypos), max(ypos), max(F)/2-(max(F))*ar/2, max(F)/2+(max(F))*ar/2])

plt.fill_between(ypos,F, 0, color='#63D2CB', alpha=.1)
plt.plot(ypos,F, color='#63D2CB', alpha=1)
plt.axis([min(ypos), max(ypos), 0, max(F)])

plt.ylabel('Cumulative Drag Force [N]')
plt.xlabel('Position along model [m]')
#plt.xticks([])
plt.savefig('fig/bins.png')
