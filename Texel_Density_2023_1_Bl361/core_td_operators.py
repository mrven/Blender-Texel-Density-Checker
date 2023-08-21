import bpy
import bmesh
import math
from datetime import datetime
from . import utils


# Calculate TD for selected polygons
class Texel_Density_Check(bpy.types.Operator):
	"""Check Density"""
	bl_idname = "object.texel_density_check"
	bl_label = "Check Texel Density"
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

		# Get Total UV area for all objects
		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0 and len(o.data.polygons) > 0:
				bpy.context.view_layer.objects.active = o
				bpy.context.view_layer.objects.active.select_set(True)

				selected_faces = []
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(bpy.context.active_object.data.polygons)

				# Select All Polygons if Calculate TD per Object and collect to list
				# if calculate TD per object
				if start_mode == 'OBJECT' or not td.selected_faces:
					for face_id in range(0, face_count):
						selected_faces.append(face_id)

				# Collect selected polygons in UV Editor
				# if call TD from UV Editor and without sync selection
				elif bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
					bpy.ops.object.mode_set(mode='EDIT')

					bm = bmesh.from_edit_mesh(o.data)
					bm.faces.ensure_lookup_table()

					for face_id in range(face_count):
						face_is_selected = True
						for loop in bm.faces[face_id].loops:
							if not loop[bm.loops.layers.uv.active].select:
								face_is_selected = False

						if face_is_selected and bm.faces[face_id].select:
							selected_faces.append(face_id)

					bpy.ops.object.mode_set(mode='OBJECT')

				# Collect selected polygons
				# if call TD from edit mode OR from UV Editor with sync selection
				else:
					bpy.ops.object.mode_set(mode='OBJECT')
					for face_id in range(0, face_count):
						if bpy.context.active_object.data.polygons[face_id].select:
							selected_faces.append(face_id)

				face_td_area_list = utils.Calculate_TD_Area_To_List()

				# Calculate Total UV Area
				for face_id in selected_faces:
					area += face_td_area_list[face_id][1]

		# Calculate Final TD
		if area > 0:
			for o in start_selected_obj:
				local_area = 0
				local_texel_density = 0

				bpy.ops.object.select_all(action='DESELECT')
				if o.type == 'MESH' and len(o.data.uv_layers) > 0 and len(o.data.polygons) > 0:
					bpy.context.view_layer.objects.active = o
					bpy.context.view_layer.objects.active.select_set(True)

					selected_faces = []
					bpy.ops.object.mode_set(mode='OBJECT')
					face_count = len(bpy.context.active_object.data.polygons)

					# Select All Polygons if Calculate TD per Object and collect to list
					# if calculate TD per object
					if start_mode == 'OBJECT' or not td.selected_faces:
						for face_id in range(0, face_count):
							selected_faces.append(face_id)

					# Collect selected polygons in UV Editor
					# if call TD from UV Editor and without sync selection
					elif bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and not bpy.context.scene.tool_settings.use_uv_select_sync:
						bpy.ops.object.mode_set(mode='EDIT')

						bm = bmesh.from_edit_mesh(o.data)
						bm.faces.ensure_lookup_table()

						for face_id in range(face_count):
							face_is_selected = True
							for loop in bm.faces[face_id].loops:
								if not loop[bm.loops.layers.uv.active].select:
									face_is_selected = False

							if face_is_selected and bm.faces[face_id].select:
								selected_faces.append(face_id)

						bpy.ops.object.mode_set(mode='OBJECT')

					# Collect selected polygons
					# if call TD from edit mode OR from UV Editor with sync selection
					else:
						bpy.ops.object.mode_set(mode='OBJECT')
						for face_id in range(0, face_count):
							if bpy.context.active_object.data.polygons[face_id].select:
								selected_faces.append(face_id)

					face_td_area_list = utils.Calculate_TD_Area_To_List()

					# Calculate UV area and TD per object
					for face_id in selected_faces:
						local_area += face_td_area_list[face_id][1]

					for face_id in selected_faces:
						local_texel_density += face_td_area_list[face_id][0] * face_td_area_list[face_id][
							1] / local_area

				# and finally calculate total TD
				texel_density += local_texel_density * local_area / area

			td.uv_space = '%.4f' % round(area * 100, 4) + ' %'
			td.density = '%.3f' % round(texel_density, 3)

		else:
			self.report({'INFO'}, "No Faces Selected or UV Area is Very Small")
			td.uv_space = '0 %'
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

		utils.Print_Execution_Time("Calculate TD", start_time)
		return {'FINISHED'}

# Set TD
class Texel_Density_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.texel_density_set"
	bl_label = "Set Texel Density"
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
					if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR' and bpy.context.screen.areas[area].ui_type == 'UV':
						ie_areas.append(area)
						flag_exist_area = True

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

				# If sync selection disabled, then select all polygons
				# It's not all polygons of object. Only selected in 3d View
				if not bpy.context.scene.tool_settings.use_uv_select_sync:
					bpy.ops.uv.select_all(action='SELECT')

				# If set each method, rescale all islands to unified TD
				# This use for single rescale factor for all
				if td.set_method == '0':
					bpy.ops.uv.average_islands_scale()

				# Calculate and get current value of TD
				bpy.ops.object.texel_density_check()
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
		bpy.ops.object.texel_density_check()

		utils.Print_Execution_Time("Set TD", start_time)
		return {'FINISHED'}

classes = (
	Texel_Density_Check,
	Texel_Density_Set,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
