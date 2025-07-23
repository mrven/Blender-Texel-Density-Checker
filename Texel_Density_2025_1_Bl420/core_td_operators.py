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

		# Save current mode and selection
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		start_selected_obj = (
			bpy.context.objects_in_mode if start_mode == 'EDIT'
			else bpy.context.selected_objects
		)

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

				selected_faces = np.array([
					f.index for f in bm.faces
					if f.select and all(loop[uv_layer].select for loop in f.loops)
				], dtype=np.int32)

				if prev_mode != 'EDIT':
					bpy.ops.object.mode_set(mode=prev_mode)

			else:
				selected_faces = np.array([
					p.index for p in mesh_data.polygons if p.select
				], dtype=np.int32)

			if selected_faces.size == 0:
				continue

			face_td_area_array = np.array(utils.Calculate_TD_Area_To_List(), dtype=np.float32)

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

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		# Get Value for TD Set
		density_new_value = 0

		# Double and Half use for buttons "Half TD" and "Double TD"
		if td.density_set != "Double" and td.density_set != "Half":
			try:
				density_new_value = float(td.density_set)
			except:
				self.report({'INFO'}, "Density value is wrong")
				return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='OBJECT')

		# Resize UV Islands for getting of target TD
		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0 and len(o.data.polygons) > 0:
				bpy.context.view_layer.objects.active = o
				bpy.context.view_layer.objects.active.select_set(True)

				# Save start selected in 3d view faces
				start_selected_faces = []
				for face_id in range(0, len(o.data.polygons)):
					if bpy.context.active_object.data.polygons[face_id].select:
						start_selected_faces.append(face_id)

				bpy.ops.object.mode_set(mode='EDIT')

				# If Set TD from UV Editor sync selection between UV Editor and 3D View
				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
					utils.Sync_UV_Selection()

				# Select All Polygons if Calculate TD per Object and collect to list
				# if calculate TD per object
				if start_mode == 'OBJECT' or not td.selected_faces:
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')

				# Check opened UV editor window(s)
				ie_areas = []
				flag_exist_area = False
				for area in range(len(bpy.context.screen.areas)):
					if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR' and bpy.context.screen.areas[
						area].ui_type == 'UV':
						ie_areas.append(area)
						flag_exist_area = True

				# Get cursor location from existing UV Editor
				ie_cursor_loc = (0, 0)

				if flag_exist_area:
					ie_cursor_loc = bpy.context.screen.areas[ie_areas[0]].spaces.active.cursor_location.copy()

				# Switch these areas to Image Editor(s)
				# because below switch active window to UV Editor
				# This guarantees only one window with UV Editor
				for ie_area in ie_areas:
					bpy.context.screen.areas[ie_area].ui_type = 'IMAGE_EDITOR'

				# Turn active window to Image Editor
				bpy.context.area.type = 'IMAGE_EDITOR'

				# if active window (now Image Editor) contains Render Result - clear that
				if bpy.context.area.spaces[0].image is not None:
					if bpy.context.area.spaces[0].image.name == 'Render Result':
						bpy.context.area.spaces[0].image = None

				# Switch Image Editor to UV Editor for manipulating with UV
				if bpy.context.space_data.mode != 'UV':
					bpy.context.space_data.mode = 'UV'

				# Save current 2D Cursor location and scale mode
				start_cursor_loc = bpy.context.area.spaces.active.cursor_location.copy()
				start_pivot_mode = bpy.context.space_data.pivot_point

				# Move 2D Cursor if used mot selection scale
				if td.rescale_anchor != 'SELECTION':
					bpy.context.space_data.pivot_point = 'CURSOR'

				if td.rescale_anchor == 'UV_CENTER':
					bpy.ops.uv.cursor_set(location=(0.5, 0.5))
				if td.rescale_anchor == 'UV_LEFT_TOP':
					bpy.ops.uv.cursor_set(location=(0, 1))
				if td.rescale_anchor == 'UV_LEFT_BOTTOM':
					bpy.ops.uv.cursor_set(location=(0, 0))
				if td.rescale_anchor == 'UV_RIGHT_TOP':
					bpy.ops.uv.cursor_set(location=(1, 1))
				if td.rescale_anchor == 'UV_RIGHT_BOTTOM':
					bpy.ops.uv.cursor_set(location=(1, 0))
				if td.rescale_anchor == '2D_CURSOR' and flag_exist_area:
					bpy.ops.uv.cursor_set(location=ie_cursor_loc)

				# If sync selection disabled, then select all polygons
				# It's not all polygons of object. Only selected in 3d View
				if not bpy.context.scene.tool_settings.use_uv_select_sync:
					bpy.ops.uv.select_all(action='SELECT')

				# If set each method, rescale all islands to unified TD
				# This use for single rescale factor for all
				if td.set_method == 'EACH':
					bpy.ops.uv.average_islands_scale()

				# Calculate and get current value of TD
				bpy.ops.texel_density.check()
				density_current_value = float(td.density)
				if density_current_value < 0.0001:
					density_current_value = 0.0001

				# Value (scale factor) for rescale islands
				if td.density_set == "Double":
					scale_fac = 2
				elif td.density_set == "Half":
					scale_fac = 0.5
				else:
					scale_fac = density_new_value / density_current_value

				# Rescale selected islands in UV Editor
				bpy.ops.transform.resize(value=(scale_fac, scale_fac, 1))

				# Restore selection mode and cursor location
				bpy.ops.uv.cursor_set(location=(start_cursor_loc.x, start_cursor_loc.y))
				bpy.context.space_data.pivot_point = start_pivot_mode

				# Switch active area to 3D View and restore UV Editor windows
				bpy.context.area.type = 'VIEW_3D'

				if flag_exist_area:
					for ie_area in ie_areas:
						bpy.context.screen.areas[ie_area].ui_type = 'UV'

				bpy.ops.mesh.select_all(action='DESELECT')

				bpy.ops.object.mode_set(mode='OBJECT')
				for face_id in start_selected_faces:
					bpy.context.active_object.data.polygons[face_id].select = True

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
