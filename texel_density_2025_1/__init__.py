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
import bpy
from bpy.app.handlers import persistent

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

@persistent
def on_load_post(_):
	props = bpy.context.scene.td
	prefs = bpy.context.preferences.addons[__package__].preferences

	if not getattr(props, "initialized", False):
		# props.td_value = prefs.default_td_value
		# props.texture_size = prefs.default_texture_size
		props.units = prefs.default_units
		props.initialized = True


def register():
	for module_name in modules_full_names.values():
		if module_name in sys.modules:
			if hasattr(sys.modules[module_name], 'register'):
				sys.modules[module_name].register()

	if on_load_post not in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append(on_load_post)


def unregister():
	if on_load_post in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(on_load_post)

	for module_name in modules_full_names.values():
		if module_name in sys.modules:
			if hasattr(sys.modules[module_name], 'unregister'):
				sys.modules[module_name].unregister()
