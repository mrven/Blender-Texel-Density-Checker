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
		props.units = prefs.default_units
		props.texture_size = prefs.default_texture_size
		if prefs.default_texture_size == 'CUSTOM':
			props.custom_width = prefs.default_custom_width
			props.custom_height = prefs.default_custom_height
		props.selected_faces = prefs.default_selected_faces
		props.checker_method = prefs.default_checker_method
		props.checker_type = prefs.default_checker_type
		props.checker_uv_scale = prefs.default_checker_uv_scale
		props.density_set = prefs.default_density_set
		props.set_method_list = prefs.default_set_method_list
		props.rescale_anchor = prefs.default_rescale_anchor
		props.select_mode = prefs.default_select_mode
		props.select_type = prefs.default_select_type
		props.select_value = prefs.default_select_value
		props.select_threshold = prefs.default_select_threshold
		# props. = prefs.default_
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
