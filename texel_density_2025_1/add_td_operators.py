import bpy
import bmesh
from bpy.props import StringProperty
from datetime import datetime
import webbrowser

from . import utils


# Copy average TD from object to object
class TexelDensityCopy(bpy.types.Operator):
	bl_idname = "texel_density.copy"
	bl_label = "TD from Active to Others"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# Save current mode and active object
		start_active_obj = context.active_object
		start_selected_obj = context.selected_objects

		# Calculate TD for active object only and copy value to "Set TD Value" field
		bpy.ops.object.select_all(action='DESELECT')
		start_active_obj.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.texel_density.check()
		td.density_set = td.density

		# Set calculated TD for all other selected objects
		for obj in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (obj.type == 'MESH' and len(obj.data.uv_layers) > 0
				and len(obj.data.polygons) > 0) and not obj == start_active_obj:
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				bpy.ops.texel_density.set()

		# Select Objects Again
		for obj in start_selected_obj:
			obj.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj

		utils.print_execution_time("Copy TD", start_time)
		return {'FINISHED'}


# Copy last calculated value of TD to "Set TD Value" field
class CalculatedToSet(bpy.types.Operator):
	bl_idname = "texel_density.calculated_to_set"
	bl_label = "Calc -> Set Value"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td
		td.density_set = td.density

		utils.print_execution_time("Calculated TD to Set", start_time)
		return {'FINISHED'}


# Copy last calculated value to "Select Value" field
class CalculatedToSelect(bpy.types.Operator):
	bl_idname = "texel_density.calculated_to_select"
	bl_label = "Calc -> Select Value"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# Copying UV area or TD depends on current select mode
		td['select_value'] = td.uv_space if td.select_mode == "ISLANDS_BY_SPACE" else td.density

		utils.print_execution_time("Calculated TD to Select", start_time)
		return {'FINISHED'}


# Buttons "Half/Double TD" and presets with values (0.64 - 20.48 px/cm)
class PresetSet(bpy.types.Operator):
	bl_idname = "texel_density.preset_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	td_value: StringProperty()

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# self.td_value is parameter
		# It's using in UI like row.operator("operator_name", text="20.48").td_value="20.48"
		if self.td_value == "Half" or self.td_value == "Double":
			# In case using buttons "Half/Double TD"
			# Store value from panel, set preset value and call Set TD
			saved_td_value = td.density_set
			td.density_set = self.td_value
			bpy.ops.texel_density.set()
			# Restore saved value
			td.density_set = saved_td_value
		else:
			td.density_set = self.td_value
			bpy.ops.texel_density.set()

		utils.print_execution_time("Preset TD Set", start_time)
		return {'FINISHED'}


# Select polygons or islands with same TD or UV space
class SelectByTDOrUVSpace(bpy.types.Operator):
	bl_idname = "texel_density.select_by_td_uv"
	bl_label = "Select Faces with same TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		start_mode = context.object.mode
		start_active_obj = context.active_object
		need_select_again_obj = context.selected_objects
		start_selected_obj = (bpy.context.objects_in_mode if start_mode == 'EDIT' else bpy.context.selected_objects)

		search_value = float(td.select_value)
		select_threshold = float(td.select_threshold)

		# Set Selection Mode to Face for 3D View and UV Editor
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
		bpy.ops.object.mode_set(mode='OBJECT')

		# Select polygons
		for obj in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if obj.type != 'MESH' or not obj.data.uv_layers or not obj.data.polygons:
				continue

			context.view_layer.objects.active = obj
			obj.select_set(True)
			face_count = len(obj.data.polygons)
			searched_faces = []

			# Get islands and TD and UV areas of each polygon
			islands_list = utils.get_uv_islands()
			face_td_area_list = utils.calculate_td_area_to_list()

			def is_in_threshold(value):
				if td.select_type == "EQUAL":
					return (search_value - select_threshold) <= value <= (search_value + select_threshold)
				elif td.select_type == "LESS":
					return value <= search_value
				elif td.select_type == "GREATER":
					return value >= search_value
				return False

			if td.select_mode == "FACES_BY_TD":
				for face_id in range(face_count):
					val = face_td_area_list[face_id][0]
					if is_in_threshold(val):
						searched_faces.append(face_id)

			elif td.select_mode in {"ISLANDS_BY_TD", "ISLANDS_BY_SPACE"}:
				for uv_island in islands_list:
					if td.select_mode == "ISLANDS_BY_TD":
						island_area = sum(face_td_area_list[face_id][1] for face_id in uv_island) or 1e-6
						island_td = sum(
							face_td_area_list[face_id][0] * face_td_area_list[face_id][1] for face_id in uv_island) / island_area
						value_to_check = island_td
					else:  # ISLANDS_BY_SPACE
						island_area = sum(face_td_area_list[face_id][1] for face_id in uv_island) * 100
						value_to_check = island_area

					if is_in_threshold(value_to_check):
						searched_faces.extend(uv_island)

			if context.area.spaces.active.type == "IMAGE_EDITOR" and not context.scene.tool_settings.use_uv_select_sync:
				bm_local = bmesh.from_edit_mesh(obj.data)
				bm_local.faces.ensure_lookup_table()
				uv_layer = bm_local.loops.layers.uv.active

				for face in bm_local.faces:
					for loop in face.loops:
						loop[uv_layer].select = False

				for face_id in searched_faces:
					for loop in bm_local.faces[face_id].loops:
						loop[uv_layer].select = True

				bmesh.update_edit_mesh(obj.data)
				bpy.ops.object.mode_set(mode='OBJECT')

			else:
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

				for face_id in searched_faces:
					obj.data.polygons[face_id].select = True

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for obj in start_selected_obj:
				context.view_layer.objects.active = obj
				bpy.ops.object.mode_set(mode='EDIT')

		context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.print_execution_time("Select by TD Space", start_time)
		return {'FINISHED'}


class OpenURL(bpy.types.Operator):
	bl_idname = "texel_density.open_url"
	bl_label = "Open URL"

	url: bpy.props.StringProperty(
		name="URL",
		description="Destination URL",
		default="https://blender.org"
	)

	def execute(self, _):
		try:
			webbrowser.open(self.url)
			return {'FINISHED'}
		except Exception as e:
			print(f"[ERROR] Failed to Open URL {self.url}: {e}")
			return {'CANCELLED'}


class ShowAddonPrefs(bpy.types.Operator):
	bl_idname = "texel_density.show_addon_prefs"
	bl_label = "Open Addon Preferences"

	def execute(self, _):
		addon_name = __name__.split('.')[0]
		bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
		bpy.context.preferences.active_section = 'ADDONS'
		bpy.ops.preferences.addon_show(module=addon_name)

		return {'FINISHED'}


classes = (
	TexelDensityCopy,
	CalculatedToSet,
	CalculatedToSelect,
	PresetSet,
	SelectByTDOrUVSpace,
	OpenURL,
	ShowAddonPrefs,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
