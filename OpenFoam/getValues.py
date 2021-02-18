#!/usr/bin/env python3.8

import numpy as np
import os
import json
import pyvista as pv
import subprocess
from PIL import Image

def pv_headless():
    pv.OFFSCREEN = True
    os.environ['DISPLAY']=':99.0'
    commands = ['Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &',
                'sleep 3',
                'exec "$@"']
    for command in commands:
        subprocess.call(command,shell=True)

def proj_area(file_name):
  pv_headless()

  model = pv.read(file_name)
  xmin,xmax,ymin,ymax,zmin,zmax = model.bounds
  A_background=(zmax-zmin)*(ymax-ymin)

  vertices = np.array([[xmin-1, ymin, zmin],
                      [xmin-1, ymin, zmax],
                      [xmin-1, ymax, zmin],
                      [xmin-1, ymax, zmax]])
  faces = np.hstack([4, 0, 1, 3, 2])
  background=pv.PolyData(vertices, faces)

  p = pv.Plotter(off_screen=True, window_size=[1000,1000])
  p.add_mesh(background, show_edges=False, color=[1,0,0], lighting=False)
  p.add_mesh(model, show_edges=False, color=[0,1,0], lighting=False)

  outfilename='fig/area.png'
  p.enable_parallel_projection()
  p.view_yz()
  p.set_background([0,0,1])
  p.show(screenshot=outfilename)

  im = Image.open(outfilename, 'r')
  pixel_values = list(im.getdata())
  model_pix=[pix for pix in pixel_values if pix==(0,255,0)]
  background_pix=[pix for pix in pixel_values if pix==(255,0,0)]
  A_model=len(model_pix)/(len(model_pix)+len(background_pix))*A_background
  
  return A_model

if os.environ.get('SIMULATION_TYPE')=='dummy':
  model_file_name='VTK/model/model_100.vtk'
else:
  model_file_name='VTK/model/model_1200.vtk'

A=proj_area(model_file_name)
U=float(os.environ.get('WIND_SPEED'))
rho=1.225
yaw=0  #read environment variable
#yaw=os.environ.get('YAW')

filename='postProcessing/forcesIncompressible/0/forces.dat'
with open(filename, 'r') as f:
    line = f.readlines()[-1].replace("(", "").replace(")", "").split()

Fd=float(line[1])+float(line[4])
Fs=float(line[2])+float(line[5])
Fl=float(line[3])+float(line[6])

Fx=Fd*np.cos(np.deg2rad(yaw))-Fs*np.sin(np.deg2rad(yaw))
Fy=Fd*np.sin(np.deg2rad(yaw))+Fs*np.cos(np.deg2rad(yaw))

CdA=2*Fd/(rho*U**2)
Cd=CdA/A

ClA=2*Fl/(rho*U**2)
Cl=ClA/A

CsA=2*Fs/(rho*U**2)
Cs=CsA/A

CxA=2*Fx/(rho*U**2)
Cx=CxA/A

CyA=2*Fy/(rho*U**2)
Cy=CyA/A

Ux=U*np.cos(np.deg2rad(yaw))
P=Fx*Ux

results = {
  "A": '%0.3f' % A,
  "Fd": '%0.2f' % Fd,
  "Fs": '%0.2f' % Fs,
  "Fl": '%0.2f' % Fl,
  "Fx": '%0.2f' % Fx,
  "Fy": '%0.2f' % Fy,
  "CdA": '%0.3f' % CdA,
  "ClA": '%0.3f' % ClA,
  "CsA": '%0.3f' % CsA,
  "CxA": '%0.3f' % CxA,
  "CyA": '%0.3f' % CyA,
  "Cd": '%0.3f' % Cd,
  "Cl": '%0.3f' % Cl,
  "Cs": '%0.3f' % Cs,
  "Cx": '%0.3f' % Cx,
  "Cy": '%0.3f' % Cy,
  "Ux": '%0.2f' % Ux,
  "P": '%0.2f' % P,
}

with open('fig/results.json', 'w') as outfile:
    json.dump(results, outfile)
