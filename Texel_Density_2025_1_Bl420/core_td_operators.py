import bpy
import bmesh
import math
from datetime import datetime
from . import utils
import numpy as np
import ctypes


# Calculate TD for selected polygons
class TexelDensityCheck(bpy.types.Operator):
	"""Check Density"""
	bl_idname = "texel_density.check"
	bl_label = "Calculate TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# Save current mode and active object
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		bpy.ops.object.mode_set(mode='OBJECT')
		area = 0
		texel_density = 0

		local_area_list = []
		local_td_list = []

		# Get Total UV area for all objects
		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0 and len(o.data.polygons) > 0:
				bpy.context.view_layer.objects.active = o
				bpy.context.view_layer.objects.active.select_set(True)

				mesh_data = o.data

				selected_faces = []
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(mesh_data.polygons)

				# Select All Polygons if Calculate TD per Object and collect to list
				# if calculate TD per object
				if start_mode == 'OBJECT' or not td.selected_faces:
					selected_faces = list(range(face_count))

				# Collect selected polygons in UV Editor
				# if call TD from UV Editor and without sync selection
				elif bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
					prev_mode = o.mode
					if prev_mode != 'EDIT':
						bpy.ops.object.mode_set(mode='EDIT')

					bm = bmesh.from_edit_mesh(mesh_data)
					bm.faces.ensure_lookup_table()
					uv_layer = bm.loops.layers.uv.active

					selected_faces = [
						f.index for f in bm.faces
						if f.select and all(loop[uv_layer].select for loop in f.loops)
					]

					if prev_mode != 'EDIT':
						bpy.ops.object.mode_set(mode=prev_mode)

				# Collect selected polygons
				# if call TD from edit mode OR from UV Editor with sync selection
				else:
					selected_faces = [p.index for p in mesh_data.polygons if p.select]

				face_td_area_list = utils.Calculate_TD_Area_To_List()

				local_area = 0
				local_texel_density = 0

				# Calculate UV area and TD per object
				for face_id in selected_faces:
					local_area += face_td_area_list[face_id][1]

				for face_id in selected_faces:
					local_texel_density += face_td_area_list[face_id][0] * face_td_area_list[face_id][1] / local_area

				# Store local Area and local TD to lists
				local_area_list.append(local_area)
				local_td_list.append(local_texel_density)

				# Calculate Total UV Area
				area += local_area

		# Calculate Final TD
		if area > 0:
			# and finally calculate total TD
			for (local_area, local_texel_density) in zip(local_area_list, local_td_list):
				texel_density += local_texel_density * local_area / area

			td.uv_space = '%.4f' % round(area * 100, 4)
			td.density = '%.3f' % round(texel_density, 3)

		else:
			self.report({'INFO'}, "No Faces Selected or UV Area is Very Small")
			td.uv_space = '0'
			td.density = '0'

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj

		for j in need_select_again_obj:
			j.select_set(True)

		utils.print_execution_time("Calculate TD", start_time)
		return {'FINISHED'}


# Set TD
class TexelDensitySet(bpy.types.Operator):
	bl_idname = "texel_density.set"
	bl_label = "Set TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# save current mode and active object
		start_active_obj = bpy.context.active_object
		start_mode = bpy.context.object.mode
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		# Get texture size from panel
		texture_size_x, texture_size_y = utils.get_texture_resolution()

		# Get Value for TD Set
		density_new_value = 0

		# Double and Half use for buttons "Half TD" and "Double TD"
		if td.density_set != "Double" and td.density_set != "Half":
			try:
				density_new_value = float(td.density_set)
			except Exception:
				self.report({'INFO'}, "Density value is wrong")
				return {'CANCELLED'}
		elif td.density_set == "Double":
			density_new_value = -2.0
		elif td.density_set == "Half":
			density_new_value = -0.5

		bpy.ops.object.mode_set(mode='OBJECT')

		# Check opened UV editor window(s)
		ie_areas = []
		flag_exist_area = False
		for area in range(len(bpy.context.screen.areas)):
			if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR' and bpy.context.screen.areas[
				area].ui_type == 'UV':
				ie_areas.append(area)
				flag_exist_area = True

		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0 and len(o.data.polygons) > 0:
				bpy.context.view_layer.objects.active = o
				bpy.context.view_layer.objects.active.select_set(True)

				mesh_data = bpy.context.active_object.data

				bpy.ops.object.mode_set(mode='OBJECT')
				obj_poly_count = len(mesh_data.polygons)

				# Select All Polygons if Calculate TD per Object and collect to list
				# if calculate TD per object
				if start_mode == 'OBJECT' or not td.selected_faces:
					selected_polygons = np.ones(obj_poly_count, dtype=np.uint8)
				elif bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
					# Array for selected loops
					uv_selection = np.empty(len(mesh_data.uv_layers.active.data), dtype=np.uint8)
					# Read selected UV
					mesh_data.uv_layers.active.data.foreach_get("select", uv_selection)
					# Array for selected polygons
					selected_polygons = np.ones(len(mesh_data.polygons), dtype=np.uint8)
					# Check selected loops in polygons
					for poly in mesh_data.polygons:
						for loop_index in poly.loop_indices:
							if not uv_selection[loop_index]:
								selected_polygons[poly.index] = 0
								break  # If not all loops selected - poly isn't selected
				# Collect selected polygons
				# if call TD from edit mode OR from UV Editor with sync selection
				else:
					bpy.ops.object.mode_set(mode='OBJECT')
					selected_polygons = np.empty(len(mesh_data.polygons), dtype=np.uint8)
					mesh_data.polygons.foreach_get("select", selected_polygons)

				if not np.any(selected_polygons):
					continue

				#Scale Origin Coordinates
				if td.rescale_anchor == 'UV_CENTER':
					origin_coordinates = (0.5, 0.5)
				elif td.rescale_anchor == 'UV_LEFT_TOP':
					origin_coordinates = (0, 1)
				elif td.rescale_anchor == 'UV_LEFT_BOTTOM':
					origin_coordinates =(0, 0)
				elif td.rescale_anchor == 'UV_RIGHT_TOP':
					origin_coordinates =(1, 1)
				elif td.rescale_anchor == 'UV_RIGHT_BOTTOM':
					origin_coordinates =(1, 0)
				elif td.rescale_anchor == '2D_CURSOR' and flag_exist_area:
					origin_coordinates =bpy.context.screen.areas[ie_areas[0]].spaces.active.cursor_location.copy()
				else:
					origin_coordinates = utils.get_average_uv_center(o, selected_polygons)

				# Each and Average Option
				scale_mode = 1 if td.set_method == 'EACH' else 0

				utils.set_texel_density_cpp(o, selected_polygons, origin_coordinates, density_new_value, texture_size_x, texture_size_y, scale_mode)

		# Select Objects Again
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		# Calculate TD for getting actual (final) value after resizing
		bpy.ops.texel_density.check()

		utils.print_execution_time("Set TD", start_time)
		return {'FINISHED'}


classes = (
	TexelDensityCheck,
	TexelDensitySet,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
