bl_info = {
	"name": "Texel Density Checker",
	"description": "Tools for for checking Texel Density and wasting of uv space",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik",
	"version": (2, 3, 1),
	"blender": (2, 81, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

'''
import bpy
import bmesh
import math
import colorsys
import blf
import bgl
import gpu
import bpy_extras.mesh_utils
import random

from gpu_extras.batch import batch_for_shader
'''

modulesNames = ['props', 'preferences', 'core_td_operators', 'add_td_operators', 'viz_operators', 'ui']

modulesFullNames = {}
for currentModuleName in modulesNames:
	modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

import sys
import importlib


draw_info = {
	"handler": None,
}

for currentModuleFullName in modulesFullNames.values():
	if currentModuleFullName in sys.modules:
		importlib.reload(sys.modules[currentModuleFullName])
	else:
		globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
		setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

def register():
	for currentModuleName in modulesFullNames.values():
		if currentModuleName in sys.modules:
			if hasattr(sys.modules[currentModuleName], 'register'):
				sys.modules[currentModuleName].register()

def unregister():
	for currentModuleName in modulesFullNames.values():
		if currentModuleName in sys.modules:
			if hasattr(sys.modules[currentModuleName], 'unregister'):
				sys.modules[currentModuleName].unregister()