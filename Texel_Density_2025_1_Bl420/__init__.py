bl_info = {
	"name": "Texel Density Checker",
	"description": "Toolset for working with Texel Density",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik, Oxicid, johnwildauer, lfod1997",
	"wiki_url": "https://github.com/mrven/Blender-Texel-Density-Checker#readme",
	"tracker_url": "https://github.com/mrven/Blender-Texel-Density-Checker/issues",
	"doc_url": "https://github.com/mrven/Blender-Texel-Density-Checker#readme",
	"version": (2025, 1, 0),
	"blender": (3, 0, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

import sys
import importlib

modules_names = ['props', 'preferences', 'utils', 'core_td_operators', 'add_td_operators', 'viz_operators', 'ui', 'test']

modules_full_names = {}
for current_module_name in modules_names:
	modules_full_names[current_module_name] = ('{}.{}'.format(__package__, current_module_name))

for current_module_full_name in modules_full_names.values():
	if current_module_full_name in sys.modules:
		importlib.reload(sys.modules[current_module_full_name])
	else:
		globals()[current_module_full_name] = importlib.import_module(current_module_full_name)
		setattr(globals()[current_module_full_name], 'modulesNames', modules_full_names)


def register():
	for module_name in modules_full_names.values():
		if module_name in sys.modules:
			if hasattr(sys.modules[module_name], 'register'):
				sys.modules[module_name].register()


def unregister():
	for module_name in modules_full_names.values():
		if module_name in sys.modules:
			if hasattr(sys.modules[module_name], 'unregister'):
				sys.modules[module_name].unregister()
