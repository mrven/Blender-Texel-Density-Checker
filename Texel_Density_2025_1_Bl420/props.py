import bpy
import os

from bpy.props import (
	StringProperty,
	EnumProperty,
	BoolProperty,
	PointerProperty,
)

from . import viz_operators
from . import utils


# Update Event Function for Changing Size of Texture
def change_texture_size(_, context):
	td = context.scene.td

	# Check exist texture image
	td_checker_texture = None
	for tex in bpy.data.images:
		if tex.is_td_texture:
			td_checker_texture = tex

	# Get texture size from panel
	checker_resolution_x, checker_resolution_y = utils.get_texture_resolution()

	if td_checker_texture:
		td_checker_texture.generated_width = checker_resolution_x
		td_checker_texture.generated_height = checker_resolution_y
		td_checker_texture.generated_type = td.checker_type

	bpy.ops.object.texel_density_check()


def change_units(_, __):
	bpy.ops.object.texel_density_check()


def change_texture_type(_, context):
	td = context.scene.td

	# Check exist texture image
	td_checker_texture = None
	for tex in bpy.data.images:
		if tex.is_td_texture:
			td_checker_texture = tex

	if td_checker_texture:
		td_checker_texture.generated_type = td.checker_type


def filter_bake_vc_min_td(_, context):
	td = context.scene.td
	bake_vc_min_td_filtered = td['bake_vc_min_td'].replace(',', '.')

	try:
		bake_vc_min_td = float(bake_vc_min_td_filtered)
	except Exception:
		bake_vc_min_td = 0.01

	if bake_vc_min_td < 0.01:
		bake_vc_min_td = 0.01

	td['bake_vc_min_td'] = str(bake_vc_min_td)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def filter_bake_vc_max_td(_, context):
	td = context.scene.td
	bake_vc_max_td_filtered = td['bake_vc_max_td'].replace(',', '.')

	try:
		bake_vc_max_td = float(bake_vc_max_td_filtered)
	except Exception:
		bake_vc_max_td = 0.01

	if bake_vc_max_td < 0.01:
		bake_vc_max_td = 0.01

	td['bake_vc_max_td'] = str(bake_vc_max_td)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def filter_bake_vc_min_space(_, context):
	td = context.scene.td
	bake_vc_min_space_filtered = td['bake_vc_min_space'].replace(',', '.')

	try:
		bake_vc_min_space = float(bake_vc_min_space_filtered)
	except Exception:
		bake_vc_min_space = 0.0001

	if bake_vc_min_space < 0.00001:
		bake_vc_min_space = 0.00001

	td['bake_vc_min_space'] = str(bake_vc_min_space)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def filter_bake_vc_distortion_range(_, context):
	td = context.scene.td
	bake_vc_min_space_filtered = td['bake_vc_distortion_range'].replace(',', '.')

	try:
		bake_vc_distortion_range = float(bake_vc_min_space_filtered)
	except Exception:
		bake_vc_distortion_range = 50

	if bake_vc_distortion_range < 1:
		bake_vc_distortion_range = 1

	td['bake_vc_distortion_range'] = str(bake_vc_distortion_range)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def filter_bake_vc_max_space(_, context):
	td = context.scene.td
	bake_vc_max_space_filtered = td['bake_vc_max_space'].replace(',', '.')

	try:
		bake_vc_max_space = float(bake_vc_max_space_filtered)
	except Exception:
		bake_vc_max_space = 0.0001

	if bake_vc_max_space < 0.00001:
		bake_vc_max_space = 0.00001

	td['bake_vc_max_space'] = str(bake_vc_max_space)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def filter_density_set(_, context):
	td = context.scene.td
	density_set_filtered = td['density_set'].replace(',', '.')

	if td.density_set != "Double" and td.density_set != "Half":
		try:
			density_set = float(density_set_filtered)
		except Exception:
			density_set = 2.0

		if density_set < 0.001:
			density_set = 0.001

		td['density_set'] = str(density_set)


def filter_checker_uv_scale(_, context):
	td = context.scene.td
	checker_uv_scale_filtered = td['checker_uv_scale'].replace(',', '.')

	try:
		checker_uv_scale = float(checker_uv_scale_filtered)
	except Exception:
		checker_uv_scale = 1

	if checker_uv_scale < 0.01:
		checker_uv_scale = 0.01

	td['checker_uv_scale'] = str(checker_uv_scale)

	try:
		td_checker_material = None
		for mat in bpy.data.materials:
			if mat.is_td_material:
				td_checker_material = mat

		if td_checker_material:
			nodes = td_checker_material.node_tree.nodes
			nodes['Mapping'].inputs['Scale'].default_value[0] = checker_uv_scale
			nodes['Mapping'].inputs['Scale'].default_value[1] = checker_uv_scale
	except Exception as e:
		print(f"[WARNING] Failed to change Checker UV Scale {e}")


def filter_select_value(_, context):
	td = context.scene.td
	select_value_filtered = td['select_value'].replace(',', '.')

	try:
		select_value = float(select_value_filtered)
	except Exception:
		select_value = 1.0

	if select_value < 0.00001:
		select_value = 0.00001

	td['select_value'] = str(select_value)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.select_by_td_space()


def filter_select_threshold(_, context):
	td = context.scene.td
	select_threshold_filtered = td['select_threshold'].replace(',', '.')

	try:
		select_threshold = float(select_threshold_filtered)
	except Exception:
		select_threshold = 0.1

	if select_threshold < 0.00001:
		select_threshold = 0.00001

	td['select_threshold'] = str(select_threshold)

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.select_by_td_space()


def change_bake_vc_mode(self, context):
	td = context.scene.td

	if td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC" or td.bake_vc_mode == "UV_SPACE_TO_VC":
		show_gradient(self, context)
	else:
		bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
		draw_info["handler"] = None

	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


def change_select_mode(_, __):
	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.select_by_td_space()


def change_uv_islands_mode(_, __):
	if utils.get_preferences().automatic_recalc:
		bpy.ops.object.bake_td_uv_to_vc()


draw_info = {
	"handler": None,
}


def show_gradient(_, context):
	td = context.scene.td
	if td.bake_vc_show_gradient and draw_info["handler"] is None:
		draw_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(viz_operators.draw_callback_px, (None, None),
																	  'WINDOW', 'POST_PIXEL')
	elif (not td.bake_vc_show_gradient) and draw_info["handler"] is not None:
		bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
		draw_info["handler"] = None


class TDAddonProps(bpy.types.PropertyGroup):
	uv_space: StringProperty(
		name="",
		description="Wasting of uv space",
		default="0 %")

	density: StringProperty(
		name="",
		description="Texel Density",
		default="0")

	density_set: StringProperty(
		name="",
		description="Texel Density",
		default="1.28",
		update=filter_density_set)

	tex_size = (('512', '512px', ''),
				('1024', '1024px', ''),
				('2048', '2048px', ''),
				('4096', '4096px', ''),
				('CUSTOM', 'Custom', ''))
	texture_size: EnumProperty(name="", items=tex_size, update=change_texture_size)

	selected_faces: BoolProperty(
		name="Selected Faces",
		description="Operate only on selected faces",
		default=True)

	custom_width: StringProperty(
		name="",
		description="Custom Width",
		default="1024",
		update=change_texture_size)

	custom_height: StringProperty(
		name="",
		description="Custom Height",
		default="1024",
		update=change_texture_size)

	units_list = (('0', 'px/cm', ''),
				  ('1', 'px/m', ''),
				  ('2', 'px/in', ''),
				  ('3', 'px/ft', ''))
	units: EnumProperty(name="", items=units_list, update=change_units)

	select_value: StringProperty(
		name="",
		description="Select Value",
		default="1.0",
		update=filter_select_value)

	select_threshold: StringProperty(
		name="",
		description="Select Threshold",
		default="0.1",
		update=filter_select_threshold)

	set_method_list = (('EACH', 'Each', ''), ('AVERAGE', 'Average', ''))
	set_method: EnumProperty(name="", items=set_method_list)

	checker_method_list = (('REPLACE', 'Replace', ''), ('STORE', 'Store and Replace', ''))
	checker_method: EnumProperty(name="", items=checker_method_list, default='STORE')

	checker_type_list = (('COLOR_GRID', 'Color Grid', ''), ('UV_GRID', 'UV Grid', ''))
	checker_type: EnumProperty(name="", items=checker_type_list, update=change_texture_type)

	checker_uv_scale: StringProperty(
		name="",
		description="UV Scale",
		default="1",
		update=filter_checker_uv_scale)

	bake_vc_min_td: StringProperty(
		name="",
		description="Min TD",
		default="0.64",
		update=filter_bake_vc_min_td)

	bake_vc_max_td: StringProperty(
		name="",
		description="Max TD",
		default="10.24",
		update=filter_bake_vc_max_td)

	bake_vc_show_gradient: BoolProperty(
		name="Show Gradient",
		description="Show Gradient in Viewport",
		default=False,
		update=show_gradient)

	bake_vc_auto_min_max: BoolProperty(
		name="Auto Min/Max Value",
		description="Auto Min/Max Value",
		default=True)

	bake_vc_mode_list = (('TD_FACES_TO_VC', 'Texel (by Face)', ''),
						 ('TD_ISLANDS_TO_VC', 'Texel (by Island)', ''),
						 ('UV_ISLANDS_TO_VC', 'UV Islands', ''),
						 ('UV_SPACE_TO_VC', 'UV Space (%)', ''),
						 ('DISTORTION', 'UV Distortion', ''))
	bake_vc_mode: EnumProperty(name="", items=bake_vc_mode_list, update=change_bake_vc_mode)

	bake_vc_min_space: StringProperty(
		name="",
		description="Min UV Space",
		default="0.0001",
		update=filter_bake_vc_min_space)

	bake_vc_max_space: StringProperty(
		name="",
		description="Max UV Space",
		default="2.0",
		update=filter_bake_vc_max_space)

	bake_vc_distortion_range: StringProperty(
		name="",
		description="Range",
		default="50",
		update=filter_bake_vc_distortion_range)

	uv_islands_to_vc_mode_list = (('ISLAND', 'By Island', ''), ('OVERLAP', 'By Overlap', ''))
	uv_islands_to_vc_mode: EnumProperty(name="", items=uv_islands_to_vc_mode_list, update=change_uv_islands_mode)

	select_mode_list = (('FACES_BY_TD', 'Faces (by Texel)', ''), ('ISLANDS_BY_TD', 'Islands (by Texel)', ''),
						('ISLANDS_BY_SPACE', 'Islands (by UV Space)', ''))
	select_mode: EnumProperty(name="", items=select_mode_list, update=change_select_mode)

	select_type_list = (('EQUAL', 'Equal To', ''), ('LESS', 'Less Than', ''), ('GREATER', 'Greater Than', ''))
	select_type: EnumProperty(name="", items=select_type_list, update=change_select_mode)

	rescale_anchor_list = (('SELECTION', 'Selection', ''),
						   ('UV_CENTER', 'UV Center', ''),
						   ('UV_LEFT_BOTTOM', 'UV Left Bottom', ''),
						   ('UV_LEFT_TOP', 'UV Left Top', ''),
						   ('UV_RIGHT_BOTTOM', 'UV Right Bottom', ''),
						   ('UV_RIGHT_TOP', 'UV Right Top', ''),
						   ('2D_CURSOR', '2D Cursor', ''))
	rescale_anchor: EnumProperty(name="", items=rescale_anchor_list)

	# Debug Property
	debug: BoolProperty(
		name="Enable Debug Mode",
		description="Enable Debug Mode",
		default=False)


classes = (
	TDAddonProps,
)


def register():
	bpy.types.Material.is_td_material = BoolProperty(
		name="Is TD Checker Material",
		description="Custom Property for Texel Density Checker",
		default=False)

	bpy.types.Image.is_td_texture = BoolProperty(
		name="Is TD Checker Texture",
		description="Custom Property for Texel Density Checker",
		default=False)

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.td = PointerProperty(type=TDAddonProps)


def unregister():
	if draw_info["handler"] is not None:
		bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
		draw_info["handler"] = None

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	del bpy.types.Image.is_td_texture
	del bpy.types.Material.is_td_material

	del bpy.types.Scene.td
