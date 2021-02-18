#!/usr/bin/env python3.8

from stl import mesh
import os
import math

# TODO: implement ground/off ground
#       maybe make it handle files with weird aspect ratios like
#       using max(l_x,l_y,l_z) instead of l_x

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
    bounds['l_x'] = bounds['maxx'] - bounds['minx']
    bounds['l_y'] = bounds['maxy'] - bounds['miny']
    bounds['l_z'] = bounds['maxz'] - bounds['minz']
    return bounds

stl_file_name='constant/triSurface/model.stl'
stl_file = mesh.Mesh.from_multi_file(stl_file_name)
bounds = get_bounds()

domain_size_upstream = 6       #number of Chord lengths
domain_size_downstream = 15     #number of Chord lengths
domain_size_side = 6           #number of Chord lengths
domain_size_top = 6            #number of Chord lengths
domain_size_bottom = 0         #number of Chord lengths
refinement_box_padding = 0.1      #padding, 0 for tight around geometry
wakerefinement_length = 3      #number of Chord lengths

U = float(os.environ.get('WIND_SPEED'))
chord_length = bounds['l_x']
rho = 1.225
mu = 1.825e-5
yplus = 1.5
layer_growth = 1.3
minLayers = 5
maxLayers = 25
maxTransitionRatio = 1.5

if os.environ.get('SIMULATION_TYPE')=='dummy':
    base_cell_size = chord_length * .4
else:
    base_cell_size = chord_length * .18

near_wall_size = base_cell_size / (2 ** 7)

# Estimate yplus and bl-thickness to get firstLayerThickness and totalLayerHeight 
# See https://www.cfd-online.com/Wiki/Y_plus_wall_distance_estimation
Re = rho * U * chord_length / mu
skin_friction = ((2 * math.log10(Re) - 0.65) ** -2.3)
wall_shear_stress = skin_friction * .5 * rho * U ** 2
friction_velocity = (wall_shear_stress / rho) ** .5
bl_thickness = 0.37 * chord_length * Re ** -.2
firstLayerThickness = yplus * mu / rho / friction_velocity

# Find nSurfaceLayers to satisfy firstLayerThickness and totalLayerHeight
for i in range(minLayers,maxLayers+1):
    layers = [firstLayerThickness * layer_growth ** n for n in range(i)]
    totalLayerHeight = sum(layers)
    finalLayerThickness = layers[-1]
    nSurfaceLayers = len(layers)
    if totalLayerHeight >= bl_thickness or finalLayerThickness * maxTransitionRatio >= near_wall_size:
        break

minThickness = firstLayerThickness * .8
transition_ratio = near_wall_size/finalLayerThickness

# blockMeshDict
domain_minx = bounds['minx'] - bounds['l_x'] * domain_size_upstream
domain_maxx = bounds['maxx'] + bounds['l_x'] * domain_size_downstream
domain_miny = bounds['miny'] - bounds['l_x'] * domain_size_side
domain_maxy = bounds['maxy'] + bounds['l_x'] * domain_size_side
domain_minz = bounds['minz'] - bounds['l_x'] * domain_size_bottom
domain_maxz = bounds['maxz'] + bounds['l_x'] * domain_size_top
n_x = round((domain_maxx - domain_minx) / base_cell_size)
n_y = round((domain_maxy - domain_miny) / base_cell_size)
n_z = round((domain_maxz - domain_minz) / base_cell_size)

# snappyHexMeshDict
refinement_minx = bounds['minx'] - bounds['l_x'] * refinement_box_padding
refinement_maxx = bounds['maxx'] + bounds['l_x'] * refinement_box_padding
refinement_miny = bounds['miny'] - bounds['l_y'] * refinement_box_padding
refinement_maxy = bounds['maxy'] + bounds['l_y'] * refinement_box_padding
refinement_minz = bounds['minz'] - bounds['l_z'] * refinement_box_padding
refinement_maxz = bounds['maxz'] + bounds['l_z'] * refinement_box_padding
refinement_maxx_wake = bounds['maxx'] + bounds['l_x'] * wakerefinement_length

if os.environ.get('SIMULATION_TYPE')=='dummy':
    addLayers = 'false'
    surfaceRefinement = 2
    boxRefinement = 0
    wakeBoxRefinement = 0
else:
    addLayers = 'true'
    surfaceRefinement = 7
    boxRefinement = 5
    wakeBoxRefinement = 4

LIM_x = domain_minx + ((domain_maxx - domain_minx)/n_x)/2
LIM_y = domain_miny + ((domain_maxy - domain_miny)/n_y)/2
LIM_z = domain_maxz - ((domain_maxz - domain_minz)/n_z)/2

# controlDict
if os.environ.get('SIMULATION_TYPE')=='dummy':
    endTime = 100
else:
    endTime = 1200

writeInterval = round(endTime/10)

# decomposeParDict
if os.environ.get('SIMULATION_TYPE')=='dummy':
    numCores = 2
else:
    numCores = 48

# Write all values to file

with open('system/blockMeshDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{domain_minx}}', str(domain_minx))
filedata = filedata.replace('{{domain_maxx}}', str(domain_maxx))
filedata = filedata.replace('{{domain_miny}}', str(domain_miny))
filedata = filedata.replace('{{domain_maxy}}', str(domain_maxy))
filedata = filedata.replace('{{domain_minz}}', str(domain_minz))
filedata = filedata.replace('{{domain_maxz}}', str(domain_maxz))
filedata = filedata.replace('{{n_x}}', str(int(n_x)))
filedata = filedata.replace('{{n_y}}', str(int(n_y)))
filedata = filedata.replace('{{n_z}}', str(int(n_z)))
with open('system/blockMeshDict', 'w') as file:
    file.write(filedata)

with open('system/snappyHexMeshDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{refinement_minx}}', str(refinement_minx))
filedata = filedata.replace('{{refinement_maxx}}', str(refinement_maxx))
filedata = filedata.replace('{{refinement_miny}}', str(refinement_miny))
filedata = filedata.replace('{{refinement_maxy}}', str(refinement_maxy))
filedata = filedata.replace('{{refinement_minz}}', str(refinement_minz))
filedata = filedata.replace('{{refinement_maxz}}', str(refinement_maxz))
filedata = filedata.replace('{{wakerefinement_maxx}}', str(refinement_maxx_wake))
filedata = filedata.replace('{{LIM_x}}', str(LIM_x))
filedata = filedata.replace('{{LIM_y}}', str(LIM_y))
filedata = filedata.replace('{{LIM_z}}', str(LIM_z))
filedata = filedata.replace('{{addLayers}}', str(addLayers))
filedata = filedata.replace('{{surfaceRefinement}}', str(int(surfaceRefinement)))
filedata = filedata.replace('{{boxRefinement}}', str(int(boxRefinement)))
filedata = filedata.replace('{{wakeBoxRefinement}}', str(int(wakeBoxRefinement)))
filedata = filedata.replace('{{nSurfaceLayers}}', str(int(nSurfaceLayers)))
filedata = filedata.replace('{{firstLayerThickness}}', str(firstLayerThickness))
filedata = filedata.replace('{{minThickness}}', str(minThickness))
with open('system/snappyHexMeshDict', 'w') as file:
    file.write(filedata)

with open('system/controlDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{endTime}}', str(int(endTime)))
filedata = filedata.replace('{{writeInterval}}', str(int(writeInterval)))
with open('system/controlDict', 'w') as file:
    file.write(filedata)

with open('system/decomposeParDict', 'r') as file :
    filedata = file.read()
filedata = filedata.replace('{{numCores}}', str(int(numCores)))
with open('system/decomposeParDict', 'w') as file:
    file.write(filedata)

'''
print('U:                     %2.1f' % U)
print('Re:                    %2.1e' % Re)
print('chord_length:          %2.3f' % chord_length)
print('base_cell_size:        %f' % base_cell_size)
print('near_wall_size:        %f' % near_wall_size)
print('firstLayerThickness:   %2.3e' % firstLayerThickness)
print('Layer growth rate:     %2.1f' % layer_growth)
print('nSurfaceLayers:        %2.0f' % nSurfaceLayers)
print('totalLayerHeight:      %f' % totalLayerHeight)
print('BL_thickness:          %f' % bl_thickness)
print('transition_ratio:      %2.3f' % transition_ratio)'''
