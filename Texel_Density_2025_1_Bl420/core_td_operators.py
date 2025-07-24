import bpy
import bmesh
import math
from datetime import datetime
from . import utils
import numpy as np
import ctypes


# Calculate TD for selected polygons
class TexelDensityCheck(bpy.types.Operator):
	bl_idname = "texel_density.check"
	bl_label = "Calculate TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# Save current mode and selection
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		start_selected_obj = (bpy.context.objects_in_mode if start_mode == 'EDIT' else bpy.context.selected_objects)

		bpy.ops.object.mode_set(mode='OBJECT')
		area = 0.0

		local_area_list = []
		local_td_list = []

		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')

			if o.type != 'MESH' or len(o.data.uv_layers) == 0 or len(o.data.polygons) == 0:
				continue

			bpy.context.view_layer.objects.active = o
			o.select_set(True)

			mesh_data = o.data
			face_count = len(mesh_data.polygons)

			if start_mode == 'OBJECT' or not td.selected_faces:
				selected_faces = np.arange(face_count, dtype=np.int32)

			elif bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
				prev_mode = o.mode
				if prev_mode != 'EDIT':
					bpy.ops.object.mode_set(mode='EDIT')

				bm = bmesh.from_edit_mesh(mesh_data)
				bm.faces.ensure_lookup_table()
				uv_layer = bm.loops.layers.uv.active

				selected_faces = np.array([f.index for f in bm.faces
					if f.select and all(loop[uv_layer].select for loop in f.loops)], dtype=np.int32)

				if prev_mode != 'EDIT':
					bpy.ops.object.mode_set(mode=prev_mode)

			else:
				selected_faces = np.array([p.index for p in mesh_data.polygons if p.select], dtype=np.int32)

			if selected_faces.size == 0:
				continue

			face_td_area_array = np.array(utils.calculate_td_area_to_list(), dtype=np.float32)

			selected_areas = face_td_area_array[selected_faces, 1]
			selected_densities = face_td_area_array[selected_faces, 0]

			local_area = selected_areas.sum()

			if local_area == 0:
				local_texel_density = 0.0001
			else:
				weights = selected_areas / local_area
				local_texel_density = np.dot(selected_densities, weights)

			local_area_list.append(local_area)
			local_td_list.append(local_texel_density)
			area += local_area

		if area > 0:
			local_area_np = np.array(local_area_list, dtype=np.float32)
			local_td_np = np.array(local_td_list, dtype=np.float32)
			texel_density = np.dot(local_td_np, local_area_np / area)

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

		for obj in need_select_again_obj:
			obj.select_set(True)

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

		start_selected_obj = (bpy.context.objects_in_mode if start_mode == 'EDIT' else bpy.context.selected_objects)

		density_new_value = 0.0

		# Parse input TD value
		if td.density_set not in {"Double", "Half"}:
			try:
				density_new_value = float(td.density_set)
			except Exception:
				self.report({'INFO'}, "Density value is wrong")
				return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='OBJECT')

		for obj in start_selected_obj:
			if obj.type != 'MESH' or len(obj.data.uv_layers) == 0 or len(obj.data.polygons) == 0:
				continue

			# Select current object
			bpy.ops.object.select_all(action='DESELECT')
			context.view_layer.objects.active = obj
			obj.select_set(True)

			mesh_data = obj.data
			start_selected_faces = np.array([
					p.index for p in mesh_data.polygons if p.select
				], dtype=np.int32)

			bpy.ops.object.mode_set(mode='EDIT')

			if context.area.spaces.active.type == "IMAGE_EDITOR" and not context.scene.tool_settings.use_uv_select_sync:
				utils.sync_uv_selection()

			if start_mode == 'OBJECT' or not td.selected_faces:
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')

			# UV Editor setup
			uv_areas = [a for a in context.screen.areas if a.type == 'IMAGE_EDITOR' and a.ui_type == 'UV']
			flag_uv_area_exists = bool(uv_areas)

			ie_cursor_loc = uv_areas[0].spaces.active.cursor_location.copy() if flag_uv_area_exists else (0, 0)

			# Set active area to UV editor
			context.area.type = 'IMAGE_EDITOR'
			if context.area.spaces.active.image and context.area.spaces.active.image.name == 'Render Result':
				context.area.spaces.active.image = None

			if context.space_data.mode != 'UV':
				context.space_data.mode = 'UV'

			start_cursor_loc = context.space_data.cursor_location.copy()
			start_pivot_mode = context.space_data.pivot_point

			# Set pivot anchor if needed
			if td.rescale_anchor != 'SELECTION':
				context.space_data.pivot_point = 'CURSOR'

			cursor_locations = {
				'UV_CENTER': (0.5, 0.5),
				'UV_LEFT_TOP': (0, 1),
				'UV_LEFT_BOTTOM': (0, 0),
				'UV_RIGHT_TOP': (1, 1),
				'UV_RIGHT_BOTTOM': (1, 0),
				'2D_CURSOR': ie_cursor_loc
			}
			if td.rescale_anchor in cursor_locations:
				bpy.ops.uv.cursor_set(location=cursor_locations[td.rescale_anchor])

			if not context.scene.tool_settings.use_uv_select_sync:
				bpy.ops.uv.select_all(action='SELECT')

			if td.set_method == 'EACH':
				bpy.ops.uv.average_islands_scale()

			bpy.ops.texel_density.check()
			try:
				density_current_value = float(td.density)
				if density_current_value < 0.0001:
					density_current_value = 0.0001
			except Exception:
				density_current_value = 1.0

			if td.density_set == "Double":
				scale_fac = 2.0
			elif td.density_set == "Half":
				scale_fac = 0.5
			else:
				scale_fac = density_new_value / density_current_value

			bpy.ops.transform.resize(value=(scale_fac, scale_fac, 1))

			# Restore cursor and pivot
			bpy.ops.uv.cursor_set(location=start_cursor_loc)
			context.space_data.pivot_point = start_pivot_mode

			context.area.type = 'VIEW_3D'

			# Restore UV Editor UI type for any changed areas
			for area in uv_areas:
				area.ui_type = 'UV'

			# Restore face selection
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.mode_set(mode='OBJECT')
			for face_id in start_selected_faces:
				mesh_data.polygons[face_id].select = True

		# Restore object selection and mode
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		for obj in need_select_again_obj:
			obj.select_set(True)
		context.view_layer.objects.active = start_active_obj

		if start_mode == 'EDIT':
			for obj in start_selected_obj:
				context.view_layer.objects.active = obj
				bpy.ops.object.mode_set(mode='EDIT')

		# Final TD check
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
