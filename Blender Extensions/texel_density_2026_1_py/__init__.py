bl_info = {
	"name": "Texel Density Checker (Python Edition)",
	"description": "Toolset for working with Texel Density",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik, Oxicid, johnwildauer, lfod1997",
	"wiki_url": "https://github.com/mrven/Blender-Texel-Density-Checker#readme",
	"tracker_url": "https://github.com/mrven/Blender-Texel-Density-Checker/issues",
	"doc_url": "https://github.com/mrven/Blender-Texel-Density-Checker#readme",
	"version": (2026, 1, 1),
	"blender": (3, 0, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

_needs_reload = "bpy" in locals()

import bpy
from bpy.app.handlers import persistent
from bpy.app import timers

from . import (
	constants,
	config_json,
	utils,
	core_td_operators,
	add_td_operators,
	props,
	viz_operators,
	ui,
	preferences,
)

if _needs_reload:
	import importlib

	constants = importlib.reload(constants)
	config_json = importlib.reload(config_json)
	utils = importlib.reload(utils)
	core_td_operators = importlib.reload(core_td_operators)
	add_td_operators = importlib.reload(add_td_operators)
	props = importlib.reload(props)
	viz_operators = importlib.reload(viz_operators)
	ui = importlib.reload(ui)
	preferences = importlib.reload(preferences)


_modules = (
	props,
	preferences,
	utils,
	core_td_operators,
	add_td_operators,
	viz_operators,
	ui,
)

def deferred_initialize():
	config_json.load_or_initialize_prefs()
	config_json.saving_enabled = True
	config_json.copy_prefs_to_props(force=_needs_reload)

	return None

@persistent
def on_load_post(_):
	config_json.load_or_initialize_prefs()
	config_json.copy_prefs_to_props()


def register():
	config_json.saving_enabled = False
	for module in _modules:
		if hasattr(module, 'register'):
			module.register()

	timers.register(deferred_initialize, first_interval=0.1)

	if on_load_post not in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append(on_load_post)


def unregister():
	if on_load_post in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(on_load_post)

	for module in reversed(_modules):
		if hasattr(module, 'unregister'):
			module.unregister()
