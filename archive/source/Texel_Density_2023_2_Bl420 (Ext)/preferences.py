import bpy

from . import ui

from .ui import VIEW3D_PT_texel_density_checker, UV_PT_texel_density_checker

from bpy.props import (
	StringProperty,
	EnumProperty,
	BoolProperty
)


def update_view3d_panel_category(self, context):
	is_panel = hasattr(bpy.types, 'VIEW3D_PT_texel_density_checker')
	category = bpy.context.preferences.addons[__package__].preferences.view3d_panel_category

	if is_panel:
		try:
			bpy.utils.unregister_class(VIEW3D_PT_texel_density_checker)
		except:
			pass
	VIEW3D_PT_texel_density_checker.bl_category = category
	bpy.utils.register_class(VIEW3D_PT_texel_density_checker)


def update_uv_panel_category(self, context):
	is_panel = hasattr(bpy.types, 'UV_PT_texel_density_checker')
	category = bpy.context.preferences.addons[__package__].preferences.uv_panel_category

	if is_panel:
		try:
			bpy.utils.unregister_class(UV_PT_texel_density_checker)
		except:
			pass

	UV_PT_texel_density_checker.bl_category = category
	bpy.utils.register_class(UV_PT_texel_density_checker)


def Filter_Gradient_Offset_X(self, context):
	offset_x_filtered = bpy.context.preferences.addons[__package__].preferences['offset_x'].replace(',', '.')

	try:
		offset_x = int(offset_x_filtered)
	except:
		offset_x = 20

	if offset_x < 0:
		offset_x = 20

	bpy.context.preferences.addons[__package__].preferences['offset_x'] = str(offset_x)
	return None


def Filter_Gradient_Offset_Y(self, context):
	offset_y_filtered = bpy.context.preferences.addons[__package__].preferences['offset_y'].replace(',', '.')

	try:
		offset_y = int(offset_y_filtered)
	except:
		offset_y = 20

	if offset_y < 0:
		offset_y = 20

	bpy.context.preferences.addons[__package__].preferences['offset_y'] = str(offset_y)
	return None


class TD_Addon_Preferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	offset_x: StringProperty(
		name="",
		description="Offset X from Anchor",
		default="60", update=Filter_Gradient_Offset_X)

	offset_y: StringProperty(
		name="",
		description="Offset Y from Anchor",
		default="30", update=Filter_Gradient_Offset_Y)

	anchor_pos_list = (('LEFT_TOP', 'Left Top', ''), ('LEFT_BOTTOM', 'Left Bottom', ''),
					   ('RIGHT_TOP', 'Right Top', ''), ('RIGHT_BOTTOM', 'Right Bottom', ''))
	anchor_pos: EnumProperty(name="", items=anchor_pos_list, default='LEFT_BOTTOM')

	automatic_recalc: BoolProperty(
		name="Calling Select/Bake VC operator after changing Mode/Value",
		description="Calling Select/Bake VC operator after changing Mode/Value",
		default=False)

	view3d_panel_category: StringProperty(
		name="",
		description="Choose a name for the category of panel (3D View)",
		default="Texel Density",
		update=update_view3d_panel_category
	)

	uv_panel_category: StringProperty(
		name="",
		description="Choose a name for the category of panel (UV Editor)",
		default="Texel Density",
		update=update_uv_panel_category
	)

	view3d_panel_category_enable: BoolProperty(
		name="View 3D TD Panel",
		description="Show/Hide View 3D View UI Panel",
		default=True)

	uv_panel_enable: BoolProperty(
		name="UV Editor TD Panel",
		description="Show/Hide UV Editor TD UI Panel",
		default=True)

	def draw(self, context):
		layout = self.layout
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


class TDObjectSetting(bpy.types.PropertyGroup):
	TriIndex: bpy.props.IntProperty(name="Tri Index", default=0)
	MatIndex: bpy.props.IntProperty(name="Material Index", default=0)


classes = (
	TD_Addon_Preferences,
	VIEW3D_PT_texel_density_checker,
	UV_PT_texel_density_checker,
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
