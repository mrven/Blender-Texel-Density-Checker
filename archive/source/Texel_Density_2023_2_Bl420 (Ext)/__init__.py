bl_info = {
	"name": "Texel Density Checker",
	"description": "Toolset for working with Texel Density",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik, Oxicid",
	"wiki_url": "https://gumroad.com/l/CEIOR",
	"tracker_url": "https://github.com/mrven/Blender-Texel-Density-Checker/issues",
	"doc_url": "https://github.com/mrven/Blender-Texel-Density-Checker#readme",
	"version": (2023, 2, 2),
	"blender": (4, 2, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

modules_names = ['props', 'preferences', 'utils', 'core_td_operators', 'add_td_operators', 'viz_operators', 'ui']

modules_full_names = {}
for current_module_name in modules_names:
	modules_full_names[current_module_name] = ('{}.{}'.format(__package__, current_module_name))

import sys
import importlib

for current_module_full_name in modules_full_names.values():
	if current_module_full_name in sys.modules:
		importlib.reload(sys.modules[current_module_full_name])
	else:
		globals()[current_module_full_name] = importlib.import_module(current_module_full_name)
		setattr(globals()[current_module_full_name], 'modulesNames', modules_full_names)


def register():
	for current_module_name in modules_full_names.values():
		if current_module_name in sys.modules:
			if hasattr(sys.modules[current_module_name], 'register'):
				sys.modules[current_module_name].register()


def unregister():
	for current_module_name in modules_full_names.values():
		if current_module_name in sys.modules:
			if hasattr(sys.modules[current_module_name], 'unregister'):
				sys.modules[current_module_name].unregister()
