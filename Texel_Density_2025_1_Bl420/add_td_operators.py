import bpy
import bmesh
from bpy.props import StringProperty
from datetime import datetime
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
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects

		# Calculate TD for active object only and copy value to "Set TD Value" field
		bpy.ops.object.select_all(action='DESELECT')
		start_active_obj.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.texel_density.check()
		td.density_set = td.density

		# Set calculated TD for all other selected objects
		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0 and len(
					x.data.polygons) > 0) and not x == start_active_obj:
				x.select_set(True)
				bpy.context.view_layer.objects.active = x
				bpy.ops.texel_density.set()

		# Select Objects Again
		for x in start_selected_obj:
			x.select_set(True)
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
		if td.select_mode == "ISLANDS_BY_SPACE":
			td['select_value'] = td.uv_space[:-2]
		else:
			td['select_value'] = td.density

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

		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		search_value = float(td.select_value)
		select_threshold = float(td.select_threshold)

		# Set Selection Mode to Face for 3D View and UV Editor
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

		bpy.ops.object.mode_set(mode='OBJECT')

		# Select polygons
		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0) and len(x.data.polygons) > 0:
				bpy.context.view_layer.objects.active = x
				bpy.context.view_layer.objects.active.select_set(True)
				face_count = len(bpy.context.active_object.data.polygons)
				searched_faces = []

				# Get islands and TD and UV areas of each polygon
				islands_list = utils.get_uv_islands()
				face_td_area_list = utils.calculate_td_area_to_list(x)

				if td.select_mode == "FACES_BY_TD":
					for face_id in range(0, face_count):
						if td.select_type == "EQUAL":
							if (face_td_area_list[face_id * 2] >= (search_value - select_threshold)) and (
									face_td_area_list[face_id * 2] <= (search_value + select_threshold)):
								searched_faces.append(face_id)

						elif td.select_type == "LESS":
							if face_td_area_list[face_id * 2] <= search_value:
								searched_faces.append(face_id)

						elif td.select_type == "GREATER":
							if face_td_area_list[face_id * 2] >= search_value:
								searched_faces.append(face_id)

				elif td.select_mode == "ISLANDS_BY_TD":
					for uv_island in islands_list:
						island_td = 0
						island_area = 0

						# Calculate total island UV area
						for face_id in uv_island:
							island_area += face_td_area_list[face_id * 2 + 1]

						if island_area == 0:
							island_area = 0.000001

						# Calculate total island TD
						for face_id in uv_island:
							island_td += face_td_area_list[face_id * 2] * face_td_area_list[face_id * 2 + 1] / island_area

						if td.select_type == "EQUAL":
							if (island_td >= (search_value - select_threshold)) and (
									island_td <= (search_value + select_threshold)):
								for face_id in uv_island:
									searched_faces.append(face_id)

						elif td.select_type == "LESS":
							if island_td <= search_value:
								for face_id in uv_island:
									searched_faces.append(face_id)

						elif td.select_type == "GREATER":
							if island_td >= search_value:
								for face_id in uv_island:
									searched_faces.append(face_id)

				elif td.select_mode == "ISLANDS_BY_SPACE":
					for uv_island in islands_list:
						island_area = 0

						# Calculate total island UV area
						for face_id in uv_island:
							island_area += face_td_area_list[face_id * 2 + 1]

						# Convert UV area to percentage
						island_area *= 100

						if td.select_type == "EQUAL":
							if (island_area >= (search_value - select_threshold)) and (
									island_area <= (search_value + select_threshold)):
								for face_id in uv_island:
									searched_faces.append(face_id)

						if td.select_type == "LESS":
							if island_area <= search_value:
								for face_id in uv_island:
									searched_faces.append(face_id)

						if td.select_type == "GREATER":
							if island_area >= search_value:
								for face_id in uv_island:
									searched_faces.append(face_id)

				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
					bpy.ops.object.mode_set(mode='EDIT')

					mesh = bpy.context.active_object.data
					bm_local = bmesh.from_edit_mesh(mesh)
					bm_local.faces.ensure_lookup_table()
					uv_layer = bm_local.loops.layers.uv.active

					# If called from UV Editor without sync selection deselect all faces
					# and select only founded faces in UV Editor
					for uv_id in range(0, len(bm_local.faces)):
						for loop in bm_local.faces[uv_id].loops:
							loop[uv_layer].select = False

					for face_id in searched_faces:
						for loop in bm_local.faces[face_id].loops:
							loop[uv_layer].select = True

					bpy.ops.object.mode_set(mode='OBJECT')

				else:
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')

					bpy.ops.object.mode_set(mode='OBJECT')

					# If called from UV Editor with sync selection or 3D View
					# deselect all faces and select only founded faces in 3D View
					for face_id in searched_faces:
						bpy.context.active_object.data.polygons[face_id].select = True

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.print_execution_time("Select by TD Space", start_time)
		return {'FINISHED'}


classes = (
	TexelDensityCopy,
	CalculatedToSet,
	CalculatedToSelect,
	PresetSet,
	SelectByTDOrUVSpace,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
