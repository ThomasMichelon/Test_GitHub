#!/usr/bin/env python3.8

import numpy as np
import os
import vtk
import pyvista as pv
import subprocess
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import math
import sys
import json

def pv_headless():
    pv.OFFSCREEN = True
    os.environ['DISPLAY']=':99.0'
    commands = ['Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &',
                'sleep 3',
                'exec "$@"']
    for command in commands:
        subprocess.call(command,shell=True)

def plot_slice(scalar,dir, loc, outfilename):
    p = pv.Plotter(off_screen=True, window_size=[3200,2400])
    p.enable_parallel_projection()
    dummy_tmp=p.add_mesh(dummy, show_edges=False, color='black', diffuse=0.5, specular=0.5, ambient=0.5)
    if dir=='Y':
        slice_normal=[0,1,0]
        slice_origin=[0, loc, 0]
        p.view_xz()
    elif dir=='Z':
        slice_normal=[0,0,1]
        slice_origin=[0, 0, loc]
        p.view_xy()
    elif dir=='X':
        slice_normal=[1,0,0]
        slice_origin=[loc, 0, 0]
        p.view_yz()
    slice = wind.slice(normal=slice_normal, origin=slice_origin)

    p.camera_set = True
    p.remove_actor(dummy_tmp)

    sargs = dict(width=0.8, vertical=False, position_x=0.1, position_y=0.05, color='black', font_family='arial', label_font_size=76, fmt="%.1f")
    if scalar=='velocity':
        p.add_mesh(slice, show_edges=False, scalars='Ux', clim=[0, float(os.environ.get('WIND_SPEED'))], cmap=colormap, opacity=opacity, lighting=False, scalar_bar_args=sargs, stitle=' ')
    elif scalar=='vorticity':
        p.add_mesh(slice, show_edges=False, scalars='vorticityx', clim=[math.floor(-maxlim), math.ceil(maxlim)], cmap=colormap, opacity=opacity, lighting=False, scalar_bar_args=sargs, stitle=' ')

    p.set_background([1,1,1])
    p.show(screenshot=outfilename)

pv_headless()

stl_file_name='constant/triSurface/model.stl'
model = pv.read(stl_file_name)
xmin,xmax,ymin,ymax,zmin,zmax = model.bounds
l_x = xmax - xmin
l_y = ymax - ymin
l_z = zmax - zmin

if os.environ.get('SIMULATION_TYPE')=='dummy':
  wind = pv.read('VTK/OpenFoam_100.vtk')
else:
  wind = pv.read('VTK/OpenFoam_1200.vtk')

dummy = pv.Cube(bounds=[xmin-l_x*.2,xmin+l_x*2, ymin, ymax, zmin, zmax])

with open('custom_colormap.json') as json_file:
    custom_cmap = ListedColormap(json.load(json_file))

if sys.argv[1]=='vor':
    # Vorticity
    maxlim=max(max(wind.get_array('vorticityx')), -min(wind.get_array('vorticityx')))
    maxlim=min(maxlim*.15,750)
    #colormap = plt.cm.get_cmap('RdBu', 100)
    colormap = custom_cmap
    opacity = [1, 1, 1, 0, 1, 1, 1]

    if sys.argv[2]=='X':
        # Vorticity X
        slice_positions=np.linspace(xmin+l_x*.05,xmax+l_x*.5, 10)
        for i, slice_position in enumerate(slice_positions):
            outfilename='fig/vorticity_%02.f.png' % i
            plot_slice('vorticity','X', slice_position, outfilename)

if sys.argv[1]=='vel':
    # Velocity
    maxlim=max(wind.get_array('Ux'))
    colormap = "magma"
    #colormap = custom_cmap
    opacity = [1, 1, 1, 1, 1, 1, 0]

    if sys.argv[2]=='Y':
        # Velocity Y
        slice_positions=np.linspace(ymax+l_y*.1,ymin-l_y*.1, 10)
        for i, slice_position in enumerate(slice_positions):
            outfilename='fig/velocity_%02.f.png' % i
            plot_slice('velocity','Y', slice_position, outfilename)

    if sys.argv[2]=='Z':
        # Velocity Z
        slice_positions=np.linspace(zmin+l_z*.1,zmax+l_z*.01, 10)
        for i, slice_position in enumerate(slice_positions):
            outfilename='fig/velocity_Z_%02.f.png' % i
            plot_slice('velocity','Z', slice_position, outfilename)

    if sys.argv[2]=='X':
        # Velocity X
        slice_positions=np.linspace(xmin-l_x*.01,xmax+l_x*.01, 10)
        for i, slice_position in enumerate(slice_positions):
            outfilename='fig/velocity_X_%02.f.png' % i
            plot_slice('velocity','X', slice_position, outfilename)
