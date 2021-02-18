#!/usr/bin/env python3.8

import stl
from stl import mesh
import math
import os

#TODO: write binary if not multi_file
#      fix the part names
#      make it read rotation

def get_bounds():
    minx_temp=[]; maxx_temp=[]; miny_temp=[]; maxy_temp=[]; minz_temp=[]; maxz_temp=[]
    for part in stl_file:
        minx_temp.append(part.x.min())
        maxx_temp.append(part.x.max())
        miny_temp.append(part.y.min())
        maxy_temp.append(part.y.max())
        minz_temp.append(part.z.min())
        maxz_temp.append(part.z.max())
    bounds = {}
    bounds['minx'] = min(minx_temp)
    bounds['maxx'] = max(maxx_temp)
    bounds['miny'] = min(miny_temp)
    bounds['maxy'] = max(maxy_temp)
    bounds['minz'] = min(minz_temp)
    bounds['maxz'] = max(maxz_temp)
    return bounds

os.rename('constant/triSurface/model.stl', 'constant/triSurface/model_orig.stl')

stl_file_name='constant/triSurface/model_orig.stl'

stl_file = mesh.Mesh.from_multi_file(stl_file_name)

#find middle
bounds = get_bounds()
middlex=(bounds['maxx']+bounds['minx'])/2
middley=(bounds['maxy']+bounds['miny'])/2
middlez=(bounds['maxz']+bounds['minz'])/2

#set scale
UNIT=os.environ.get('UNIT')
if UNIT=='mm':
    scale=0.001
elif UNIT=='inches':
    scale=0.0254
else:
    scale=1

#set rotation
rotate_x=0
rotate_y=0
rotate_z=0

stl_file = mesh.Mesh.from_multi_file(stl_file_name) #why I have to do this line again I dont know

new_stl_file = open('constant/triSurface/model.stl', 'wb')
for part in stl_file:
    part.x=part.x-middlex
    part.y=part.y-middley
    part.z=part.z-middlez

    part.points = part.points*scale

    part.rotate([1, 0, 0], math.radians(rotate_x))
    part.rotate([0, 1, 0], math.radians(rotate_y))
    part.rotate([0, 0, 1], math.radians(rotate_z))

    part.save(part.name, new_stl_file) #mode=stl.Mode.ASCII
new_stl_file.close()
