#!/usr/bin/env python3.8

import os, shutil
import sys
import vtk
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pygltflib.utils import gltf2glb
import json

def export(p, basename):
    #Export a single mesh to glb format.

    if os.path.exists('export/'):
        shutil.rmtree("export/")
    os.makedirs("export/")
    exp = vtk.vtkGLTFExporter()
    exp.SetInput(p.ren_win)
    exp.SetActiveRenderer(p.renderer)
    exp.SetFileName("export/{}.gltf".format(basename))
    exp.Write()

    p.close()

    gltf2glb("export/{}.gltf".format(basename))
    shutil.move("export/{}.glb".format(basename), "{}.glb".format(basename))
    shutil.rmtree("export/")
    return True
####

if os.environ.get('SIMULATION_TYPE')=='dummy':
  pressure = pv.read('VTK/model/model_100.vtk')
else:
  pressure = pv.read('VTK/model/model_1200.vtk')

#colormap = plt.cm.get_cmap('magma', 100)
with open('custom_colormap.json') as json_file:
    custom_cmap = ListedColormap(json.load(json_file))
colormap=custom_cmap

maxlim=max(max(pressure.get_array('total(p)_coeff')), -min(pressure.get_array('total(p)_coeff')))/2

p=pv.Plotter()
p.add_mesh(pressure, show_edges=False, scalars='total(p)_coeff', clim=[-maxlim, maxlim], cmap=colormap)
p.view_vector([-1,-1,0])
p.set_background([1,1,1])

export(p, 'pressure')
shutil.move('pressure.glb', 'fig/pressure.glb')
