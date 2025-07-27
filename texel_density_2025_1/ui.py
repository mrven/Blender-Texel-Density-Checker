import bpy

from . import utils
from . import core_td_operators, add_td_operators, viz_operators
from .constants import *

def panel_draw(layout, context):
	td = context.scene.td
	is_view_3d_panel = context.area.type == 'VIEW_3D'

	if context.active_object.type == 'MESH' and len(context.active_object.data.uv_layers) > 0:
		row = layout.row(align=True)
		row.label(text="Units:")
		row.prop(td, 'units', expand=False)

		box = layout.box()
		row = box.row(align=True)
		row.label(text="Texture Size:")
		row.prop(td, 'texture_size', expand=False)

		# If custom texture size show fields for width and height
		if td.texture_size == 'CUSTOM':
			row = box.row(align=True)
			row.label(text="Width:")
			row.prop(td, "custom_width")
			row.label(text=" px")

			row = box.row(align=True)
			row.label(text="Height:")
			row.prop(td, "custom_height")
			row.label(text=" px")

		if is_view_3d_panel:
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Checker Method:")
			row.prop(td, 'checker_method', expand=False)

			row = box.row(align=True)
			row.label(text="Checker Type:")
			row.prop(td, 'checker_type', expand=False)

			row = box.row(align=True)
			row.label(text="UV Scale:")
			row.prop(td, 'checker_uv_scale')

			row = box.row()
			row.operator(viz_operators.CheckerAssign.bl_idname)

			# If Checker Method "Store and Replace"
			if td.checker_method == 'STORE':
				row = box.row()
				row.operator(viz_operators.CheckerRestore.bl_idname)
				row = box.row()
				row.operator(viz_operators.ClearSavedMaterials.bl_idname)

		if context.object.mode == 'EDIT':
			box = layout.box()
			row = box.row()
			if td.selected_faces:
				row.prop(td, "selected_faces", text="Selected Faces", icon="CHECKBOX_HLT")
			else:
				row.prop(td, "selected_faces", text="Selected Faces", icon="CHECKBOX_DEHLT")

		box = layout.box()
		row = box.row(align=True)
		row.label(text="UV Space:")
		row.label(text=f"{td.uv_space} %")

		cur_units = td.units_list[int(td.units)][1]

		row = box.row(align=True)
		row.label(text="Density:")
		row.label(text=f"{td.density} {cur_units}")

		row = box.row()
		row.operator(core_td_operators.TexelDensityCheck.bl_idname)
		row = box.row()
		row.operator(add_td_operators.CalculatedToSet.bl_idname)
		if context.object.mode == 'EDIT':
			row = box.row()
			row.operator(add_td_operators.CalculatedToSelect.bl_idname)

		box = layout.box()
		row = box.row(align=True)
		row.label(text="Set TD:")
		row.prop(td, "density_set")
		row.label(text=f" {cur_units}")

		row = box.row(align=True)
		row.label(text="Set Method:")
		row.prop(td, 'set_method', expand=False)

		row = box.row(align=True)
		row.label(text="Scale Anchor:")
		row.prop(td, 'rescale_anchor', expand=False)

		row = box.row()
		row.operator(core_td_operators.TexelDensitySet.bl_idname)

		# Preset Buttons
		preset_rows = PRESET_VALUES.get(td.units)
		if preset_rows:
			for preset_row in preset_rows:
				row = box.row(align=True)
				for val in preset_row:
					op = row.operator(add_td_operators.PresetSet.bl_idname, text=val)
					op.td_value = val

		row = box.row(align=True)
		row.operator(add_td_operators.PresetSet.bl_idname, text="Half TD").td_value = "Half"
		row.operator(add_td_operators.PresetSet.bl_idname, text="Double TD").td_value = "Double"

		if context.object.mode == 'OBJECT':
			row = layout.row()
			row.operator(add_td_operators.TexelDensityCopy.bl_idname)

		if context.object.mode == 'EDIT':
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Select:")
			row.prop(td, "select_mode", expand=False)

			row = box.row(align=True)
			row.label(text="Select Type:")
			row.prop(td, "select_type", expand=False)

			row = box.row(align=True)
			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				row.label(text="Texel:")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.label(text="UV Space:")

			row.prop(td, "select_value")

			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				row.label(text=" " + cur_units)
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.label(text=" %")

			if td.select_type == "EQUAL":
				row = box.row(align=True)
				row.label(text="Select Threshold:")
				row.prop(td, "select_threshold")

			row = box.row()
			if td.select_mode == "FACES_BY_TD":
				row.operator(add_td_operators.SelectByTDOrUVSpace.bl_idname, text="Select Faces By TD")
			elif td.select_mode == "ISLANDS_BY_TD":
				row.operator(add_td_operators.SelectByTDOrUVSpace.bl_idname, text="Select Islands By TD")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.operator(add_td_operators.SelectByTDOrUVSpace.bl_idname, text="Select Islands By UV Space")

		if is_view_3d_panel:
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Bake VC Mode:")
			row.prop(td, "bake_vc_mode", expand=False)

			if td.bake_vc_mode in {"TD_FACES_TO_VC", "TD_ISLANDS_TO_VC"}:
				row = box.row()
				if td.bake_vc_auto_min_max:
					row.prop(td, "bake_vc_auto_min_max", text="Auto Min/Max Value", icon="CHECKBOX_HLT")
				else:
					row.prop(td, "bake_vc_auto_min_max", text="Auto Min/Max Value", icon="CHECKBOX_DEHLT")

				row = box.row(align=True)
				row.label(text="Min TD Value:")
				row.label(text="Max TD Value:")

				row = box.row(align=True)
				row.prop(td, "bake_vc_min_td")
				row.prop(td, "bake_vc_max_td")

			if td.bake_vc_mode == "UV_SPACE_TO_VC":
				row = box.row(align=True)
				row.label(text="Min UV Space:")
				row.label(text="Max UV Space:")

				row = box.row(align=True)
				row.prop(td, "bake_vc_min_space")
				row.prop(td, "bake_vc_max_space")

			if td.bake_vc_mode == "UV_ISLANDS_TO_VC":
				row = box.row(align=True)
				row.label(text="Island Detect Mode:")
				row.prop(td, "uv_islands_to_vc_mode", expand=False)

			if td.bake_vc_mode == 'DISTORTION':
				row = box.row(align=True)
				row.label(text="Range:")
				row.prop(td, "bake_vc_distortion_range")
				row.label(text=" %")

			if td.bake_vc_mode in {"TD_FACES_TO_VC", "TD_ISLANDS_TO_VC", "UV_SPACE_TO_VC", 'DISTORTION'}:
				row = box.row()
				if td.bake_vc_show_gradient:
					row.prop(td, "bake_vc_show_gradient", text="Show Gradient", icon="CHECKBOX_HLT")
				else:
					row.prop(td, "bake_vc_show_gradient", text="Show Gradient", icon="CHECKBOX_DEHLT")

			if td.bake_vc_mode in {"TD_FACES_TO_VC", "TD_ISLANDS_TO_VC"}:
				row = box.row()
				row.operator(viz_operators.BakeTDToVC.bl_idname, text="Texel Density to VC")

			if td.bake_vc_mode == "UV_SPACE_TO_VC":
				row = box.row()
				row.operator(viz_operators.BakeTDToVC.bl_idname, text="UV Space to VC")

			if td.bake_vc_mode == "UV_ISLANDS_TO_VC":
				row = box.row()
				row.operator(viz_operators.BakeTDToVC.bl_idname, text="UV Islands to VC")

			if td.bake_vc_mode == 'DISTORTION':
				row = box.row()
				row.operator(viz_operators.BakeTDToVC.bl_idname, text="UV Distortion to VC")

			row = box.row()
			row.operator(viz_operators.ClearTDFromVC.bl_idname)

	else:
		if not context.active_object.type == 'MESH':
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Active object isn't a mesh", icon='ERROR')
		elif len(context.active_object.data.uv_layers) == 0:
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Mesh doesn't have any UV", icon='ERROR')


# Panel in 3D View
class TDAddonView3DPanel(bpy.types.Panel):
	bl_idname = "VIEW3D_PT_texel_density_checker"
	bl_label = "Texel Density Checker"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Texel Density"

	@classmethod
	def poll(cls, context):
		preferences = utils.get_preferences()
		return (context.object is not None) and (context.active_object is not None) and preferences.view3d_panel_category_enable

	def draw(self, context):
		panel_draw(self.layout, context)


# Panel in UV Editor
class TDAddonUVPanel(bpy.types.Panel):
	bl_idname = "UV_PT_texel_density_checker"
	bl_label = "Texel Density Checker"
	bl_space_type = "IMAGE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Texel Density"

	@classmethod
	def poll(cls, context):
		preferences = utils.get_preferences()
		return ((context.object is not None) and (context.active_object is not None) and context.mode == 'EDIT_MESH' and preferences.uv_panel_enable
				and context.space_data.mode == 'UV')

	def draw(self, context):
		panel_draw(self.layout, context)
