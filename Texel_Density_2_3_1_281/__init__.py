bl_info = {
	"name": "Texel Density Checker",
	"description": "Tools for for checking Texel Density and wasting of uv space",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik",
	"version": (2, 3, 1),
	"blender": (2, 81, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

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

from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        )
		
from bpy.props import (
		StringProperty,
		EnumProperty,
        BoolProperty,
        PointerProperty,
        )

from . import core_td_operators
from . import add_td_operators
from . import viz_operators
from . import ui
from . import props
from . import preferences

draw_info = {
	"handler": None,
}

classes = (
    VIEW3D_PT_texel_density_checker,
    UI_PT_texel_density_checker,
    TD_Addon_Preferences,
	TD_Addon_Props,
	Texel_Density_Check,
	Texel_Density_Set,
	Texel_Density_Copy,
	Calculated_To_Set,
	Preset_Set,
	Select_Same_TD,
	Checker_Assign,
	Checker_Restore,
	Clear_Object_List,
	Bake_TD_UV_to_VC,
	Clear_TD_VC,
)	

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.types.Scene.td = PointerProperty(type=TD_Addon_Props)

def unregister():
	if draw_info["handler"] != None:
		bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
		draw_info["handler"] = None

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
		
	del bpy.types.Scene.td

if __name__ == "__main__":
	register()