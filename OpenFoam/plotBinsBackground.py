#!/usr/bin/env python3.8

import numpy as np
import os
import vtk
import pyvista as pv
import subprocess
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL import Image

def pv_headless():
    pv.OFFSCREEN = True
    os.environ['DISPLAY']=':99.0'
    commands = ['Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &',
                'sleep 3',
                'exec "$@"']
    for command in commands:
        subprocess.call(command,shell=True)

def bbox(im):
    a = np.array(im)[:,:,:3]  # keep RGB only
    m = np.any(a != [255, 255, 255], axis=2)
    coords = np.argwhere(m)
    y0, x0, y1, x1 = *np.min(coords, axis=0), *np.max(coords, axis=0)
    return (x0, y0, x1+1, y1+1)

pv_headless()

stl_file_name='constant/triSurface/model.stl'
model=pv.read(stl_file_name)
xmin,xmax,ymin,ymax,zmin,zmax = model.bounds

p = pv.Plotter(off_screen=True, window_size=[1024,1024])
p.add_mesh(model, show_edges=False, color='white', diffuse=0.5, specular=0.5, ambient=0.5)

p.enable_parallel_projection()
p.view_xz()

p.set_background([1,1,1])
outfilename='fig/binsbackground.png'
p.show(screenshot=outfilename)

im = Image.open(outfilename)
im2 = im.crop(bbox(im))
im2.save(outfilename)
