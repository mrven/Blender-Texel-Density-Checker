import bpy
from bpy.props import (
	StringProperty,
	EnumProperty,
	BoolProperty
)

from . import ui
from .ui import TDAddonView3DPanel, TDAddonUVPanel
from . import config_json
from .constants import *

def update_view3d_panel_category(_, __):
	is_panel = hasattr(bpy.types, 'VIEW3D_PT_texel_density_checker')
	category = bpy.context.preferences.addons[__package__].preferences.view3d_panel_category

	if is_panel:
		try:
			bpy.utils.unregister_class(TDAddonView3DPanel)
		except Exception as e:
			print(f"[WARNING] Failed to unregister panel {e}")
			pass
	TDAddonView3DPanel.bl_category = category
	bpy.utils.register_class(TDAddonView3DPanel)
	config_json.save_addon_prefs()


def update_uv_panel_category(_, __):
	is_panel = hasattr(bpy.types, 'UV_PT_texel_density_checker')
	category = bpy.context.preferences.addons[__package__].preferences.uv_panel_category

	if is_panel:
		try:
			bpy.utils.unregister_class(TDAddonUVPanel)
		except Exception as e:
			print(f"[WARNING] Failed to unregister panel {e}")
			pass

	TDAddonUVPanel.bl_category = category
	bpy.utils.register_class(TDAddonUVPanel)
	config_json.save_addon_prefs()


def filter_gradient_offset_x(self, __):
	offset_x_filtered = self.offset_x.replace(',', '.')

	try:
		offset_x = int(offset_x_filtered)
	except Exception:
		offset_x = 20

	if offset_x < 0:
		offset_x = 20

	if not str(offset_x) == self.offset_x:
		self.offset_x = str(offset_x)
	config_json.save_addon_prefs()
	return None


def filter_gradient_offset_y(self, __):
	offset_y_filtered = self.offset_y.replace(',', '.')

	try:
		offset_y = int(offset_y_filtered)
	except Exception:
		offset_y = 20

	if offset_y < 0:
		offset_y = 20

	if not str(offset_y) == self.offset_y:
		self.offset_y = str(offset_y)
	config_json.save_addon_prefs()
	return None


def update_save_config(_, __):
	config_json.save_addon_prefs()


class TDAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	offset_x: StringProperty(
		name="",
		description="Offset X from Anchor",
		default="60", update=filter_gradient_offset_x)

	offset_y: StringProperty(
		name="",
		description="Offset Y from Anchor",
		default="30", update=filter_gradient_offset_y)

	anchor_pos: EnumProperty(name="", items=PREFS_ANCHOR_ITEMS, default='LEFT_BOTTOM', update=update_save_config)

	automatic_recalc: BoolProperty(
		name="Calling Select/Bake VC operator after changing Mode/Value",
		description="Calling Select/Bake VC operator after changing Mode/Value",
		default=False,
		update=update_save_config)

	calculation_backend: EnumProperty(name="", items=PREFS_BACKEND_ITEMS, default='CPP', update=update_save_config)

	view3d_panel_category: StringProperty(
		name="",
		description="Choose a name for the category of panel (3D View)",
		default="Texel Density",
		update=update_view3d_panel_category)

	uv_panel_category: StringProperty(
		name="",
		description="Choose a name for the category of panel (UV Editor)",
		default="Texel Density",
		update=update_save_config)

	view3d_panel_category_enable: BoolProperty(
		name="View 3D TD Panel",
		description="Show/Hide View 3D View UI Panel",
		default=True,
		update=update_save_config)

	uv_panel_enable: BoolProperty(
		name="UV Editor TD Panel",
		description="Show/Hide UV Editor TD UI Panel",
		default=True,
		update=update_save_config)

	# Defaults
	default_units: EnumProperty(name="", items=TD_UNITS_ITEMS, update=update_save_config)

	default_texture_size: EnumProperty(name="", items=TD_TEXTURE_SIZE_ITEMS, update=update_save_config)

	default_custom_width: StringProperty(name="W", default="1024", update=update_save_config)

	default_custom_height: StringProperty(name="  H", default="1024", update=update_save_config)

	default_selected_faces: BoolProperty(name="", default=True, update=update_save_config)

	default_checker_method: EnumProperty(
		name="",
		items=TD_CHECKER_METHOD_ITEMS,
		default='STORE',
		update=update_save_config)

	default_checker_type: EnumProperty(name="", items=TD_CHECKER_TYPE_ITEMS, update=update_save_config)

	default_checker_uv_scale: StringProperty(name="", default="1", update=update_save_config)

	default_density_set: StringProperty(name="", default="1.28", update=update_save_config)

	default_set_method: EnumProperty(name="", items=TD_SET_METHOD_ITEMS, update=update_save_config)

	default_rescale_anchor: EnumProperty(name="", items=TD_ANCHOR_ORIGIN_ITEMS, update=update_save_config)

	default_select_mode: EnumProperty(name="", items=TD_SELECT_MODE_ITEMS, update=update_save_config)

	default_select_type: EnumProperty(name="", items=TD_SELECT_TYPE_ITEMS, update=update_save_config)

	default_select_value: StringProperty(name="", default="1.0", update=update_save_config)

	default_select_threshold: StringProperty(name="", default="0.1", update=update_save_config)

	default_bake_vc_mode: EnumProperty(name="", items=TD_BAKE_VC_MODE_ITEMS, update=update_save_config)

	default_bake_vc_auto_min_max: BoolProperty(name="", default=True, update=update_save_config)

	default_bake_vc_min_td: StringProperty(name="Min", default="0.64", update=update_save_config)

	default_bake_vc_max_td: StringProperty(name="   Max", default="10.24", update=update_save_config)

	default_uv_islands_to_vc_mode: EnumProperty(name="", items=TD_BAKE_UV_ISLANDS_MODE_ITEMS, update=update_save_config)

	default_bake_vc_min_space: StringProperty(name="Min", default="0.1", update=update_save_config)

	default_bake_vc_max_space: StringProperty(name="   Max", default="25.0", update=update_save_config)

	default_bake_vc_distortion_range: StringProperty(name="", default="50", update=update_save_config)

	default_bake_vc_show_gradient: BoolProperty(name="", default=False, update=update_save_config)


	def draw(self, _):
		layout = self.layout
		box = layout.box()
		row = box.row(align=True)
		row.label(text='Calculation Backend:')
		row.prop(self, 'calculation_backend', expand=False)

		box = layout.box()
		row = box.row()
		row.label(text='Default Settings:')
		row = box.row(align=True)
		row.label(text='Units:')
		row.prop(self, 'default_units')
		row = box.row(align=True)
		row.label(text='Texture Size:')
		row.prop(self, 'default_texture_size')
		if self.default_texture_size == 'CUSTOM':
			row = box.row(align=True)
			row.label(text='   Custom Size:')
			row.prop(self, 'default_custom_width')
			row.prop(self, 'default_custom_height')
		box.separator(factor=0.5)
		row = box.row(align=True)
		row.label(text='Selected Faces:')
		row.prop(self, 'default_selected_faces')
		box.separator(factor=0.5)
		row = box.row(align=True)
		row.label(text='Checker Method:')
		row.prop(self, 'default_checker_method')
		row = box.row(align=True)
		row.label(text='Checker Type:')
		row.prop(self, 'default_checker_type')
		row = box.row(align=True)
		row.label(text='Checker UV Scale:')
		row.prop(self, 'default_checker_uv_scale')
		box.separator(factor=0.5)
		row = box.row(align=True)
		row.label(text='Set TD Value:')
		row.prop(self, 'default_density_set')
		row = box.row(align=True)
		row.label(text='Set Method:')
		row.prop(self, 'default_set_method')
		row = box.row(align=True)
		row.label(text='Scale Anchor Origin:')
		row.prop(self, 'default_rescale_anchor')
		box.separator(factor=0.5)
		row = box.row(align=True)
		row.label(text='Select Mode:')
		row.prop(self, 'default_select_mode')
		row = box.row(align=True)
		row.label(text='Select Type:')
		row.prop(self, 'default_select_type')
		row = box.row(align=True)
		row.label(text='Select Value:')
		row.prop(self, 'default_select_value')
		if self.default_select_type == 'EQUAL':
			row = box.row(align=True)
			row.label(text='Select Threshold:')
			row.prop(self, 'default_select_threshold')
		box.separator(factor=0.5)
		row = box.row(align=True)
		row.label(text='Bake VC Mode:')
		row.prop(self, 'default_bake_vc_mode')
		if self.default_bake_vc_mode in {'TD_FACES_TO_VC', 'TD_ISLANDS_TO_VC'}:
			row = box.row(align=True)
			row.label(text='Auto Min/Max Value:')
			row.prop(self, 'default_bake_vc_auto_min_max')
			row = box.row(align=True)
			row.prop(self, 'default_bake_vc_min_td')
			row.prop(self, 'default_bake_vc_max_td')
		if self.default_bake_vc_mode == 'UV_ISLANDS_TO_VC':
			row = box.row(align=True)
			row.label(text='Island Detect Mode:')
			row.prop(self, 'default_uv_islands_to_vc_mode')
		if self.default_bake_vc_mode == 'UV_SPACE_TO_VC':
			row = box.row(align=True)
			row.prop(self, 'default_bake_vc_min_space')
			row.prop(self, 'default_bake_vc_max_space')
		if self.default_bake_vc_mode == 'DISTORTION':
			row = box.row(align=True)
			row.label(text='Distortion Range:')
			row.prop(self, 'default_bake_vc_distortion_range')
		if self.default_bake_vc_mode in {'TD_FACES_TO_VC',
										 'TD_ISLANDS_TO_VC',
										 'UV_SPACE_TO_VC',
										 'DISTORTION'}:
			row = box.row(align=True)
			row.label(text='Show Gradient:')
			row.prop(self, 'default_bake_vc_show_gradient')

		box.separator(factor=0.5)
		row = box.row()
		row.operator(ApplyDefaultsToProps.bl_idname, text='Apply Default Settings')

		box = layout.box()
		row = box.row()
		row.label(text='Texel Density Gradient Position:')
		row = box.row(align=True)
		row.label(text='Position Anchor:')
		row.prop(self, 'anchor_pos', expand=False)
		row = box.row(align=True)
		row.label(text='Offset X:')
		row.prop(self, 'offset_x')
		row = box.row(align=True)
		row.label(text='Offset Y:')
		row.prop(self, 'offset_y')

		box = layout.box()
		row = box.row(align=True)
		row.prop(self, 'view3d_panel_category_enable')
		if self.view3d_panel_category_enable:
			row.prop(self, 'view3d_panel_category', text="Panel")
		row = box.row(align=True)
		row.prop(self, 'uv_panel_enable')
		if self.uv_panel_enable:
			row.prop(self, 'uv_panel_category', text="Panel")

		layout.prop(self, 'automatic_recalc')

		layout.separator(factor=0.5)
		row = layout.row()
		row.operator(ResetPreferences.bl_idname, text='Reset Preferences')

class TDObjectSetting(bpy.types.PropertyGroup):
	mat_index: bpy.props.IntProperty(name="Material Index", default=0)


class ResetPreferences(bpy.types.Operator):
	"""Reset all preferences to default values"""
	bl_idname = "texel_density.reset_preferences"
	bl_label = "Reset Preferences"

	def execute(self, context):
		prefs = context.preferences.addons[__package__].preferences

		prefs.default_checker_uv_scale = "10.0"

		self.report({'INFO'}, "Preferences was successfully reset.")
		return {'FINISHED'}


class ApplyDefaultsToProps(bpy.types.Operator):
	"""Apply current defaults from preferences to props"""
	bl_idname = "texel_density.apply_defaults_to_props"
	bl_label = "Apply Default Settings"

	def execute(self, _):
		config_json.copy_prefs_to_props(force=True)
		return {'FINISHED'}



classes = (
	ApplyDefaultsToProps,
	ResetPreferences,
	TDAddonPreferences,
	TDAddonView3DPanel,
	TDAddonUVPanel,
	TDObjectSetting
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Object.td_settings = bpy.props.CollectionProperty(type=TDObjectSetting)
	# Update Category
	context = bpy.context
	prefs = bpy.context.preferences.addons[__package__].preferences
	update_view3d_panel_category(prefs, context)
	update_uv_panel_category(prefs, context)


def unregister():
	del bpy.types.Object.td_settings
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
