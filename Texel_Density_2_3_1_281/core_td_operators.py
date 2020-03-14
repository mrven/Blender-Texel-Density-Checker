import bpy
import bmesh
import math

from . import utils


class Texel_Density_Check(bpy.types.Operator):
	"""Check Density"""
	bl_idname = "object.texel_density_check"
	bl_label = "Check Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		td = context.scene.td
		
		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_mode = bpy.context.object.mode

		#set default values
		area=0
		gm_area = 0
		texture_size_cur_x = 1024
		texture_size_cur_y = 1024
		
		#Get texture size from panel
		if td.texture_size == '0':
			texture_size_cur_x = 512
			texture_size_cur_y = 512
		if td.texture_size == '1':
			texture_size_cur_x = 1024
			texture_size_cur_y = 1024
		if td.texture_size == '2':
			texture_size_cur_x = 2048
			texture_size_cur_y = 2048
		if td.texture_size == '3':
			texture_size_cur_x = 4096
			texture_size_cur_y = 4096
		if td.texture_size == '4':
			try:
				texture_size_cur_x = int(td.custom_width)
			except:
				texture_size_cur_x = 1024
			try:
				texture_size_cur_y = int(td.custom_height)
			except:
				texture_size_cur_y = 1024

		if texture_size_cur_x < 1 or texture_size_cur_y < 1:
			texture_size_cur_x = 1024
			texture_size_cur_y = 1024

		aspect_ratio = texture_size_cur_x / texture_size_cur_y;
		if aspect_ratio < 1:
			aspect_ratio = 1 / aspect_ratio
		largest_side = texture_size_cur_x if texture_size_cur_x > texture_size_cur_y else texture_size_cur_y;

		bpy.ops.object.mode_set(mode='OBJECT')

		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0:
				o.select_set(True)
				bpy.context.view_layer.objects.active = o
				#Duplicate and Triangulate Object
				bpy.ops.object.duplicate()
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

				bpy.ops.object.mode_set(mode='EDIT')
				
				#Select All Polygons if Calculate TD per Object
				if start_mode == 'OBJECT' or td.selected_faces == False:
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')

				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
					utils.Sync_UV_Selection()

				#Get selected list of selected polygons
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(bpy.context.active_object.data.polygons)
				selected_faces = []
				for face_id in range (0, face_count):
					if bpy.context.active_object.data.polygons[face_id].select == True:
						selected_faces.append(face_id)
				
				#get bmesh from active object		
				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()
				for x in selected_faces:
					#set default values for multiplication of vectors (uv and physical area of object)
					local_area = 0
					#UV Area calculating
					#get uv-coordinates of verteces of current triangle
					for tri_index in range(0, len(bm.faces[x].loops) - 2):
						loop_a = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
						loop_b = bm.faces[x].loops[tri_index + 1][bm.loops.layers.uv.active].uv
						loop_c = bm.faces[x].loops[tri_index + 2][bm.loops.layers.uv.active].uv
						#get multiplication of vectors of current triangle
						multi_vector = utils.Vector2d_Multiply(loop_a, loop_b, loop_c)
						#Increment area of current tri to total uv area
						local_area += 0.5 * multi_vector

					gm_area += bpy.context.active_object.data.polygons[x].area
					area += local_area

				#delete duplicated object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.delete()

		#Calculate TD and Display Value
		if area > 0:
			#UV Area in percents
			uv_space = area * 100
			
			#TexelDensity calculating from selected in panel texture size
			if gm_area > 0:
				texel_density = ((largest_side / math.sqrt(aspect_ratio)) * math.sqrt(area))/(math.sqrt(gm_area)*100) / bpy.context.scene.unit_settings.scale_length
			else:
				texel_density = 0.001

			#show calculated values on panel
			td.uv_space = '%.3f' % round(uv_space, 3) + ' %'
			if td.units == '0':
				td.density = '%.3f' % round(texel_density, 3)
			if td.units == '1':
				td.density = '%.3f' % round(texel_density*100, 3)
			if td.units == '2':
				td.density = '%.3f' % round(texel_density*2.54, 3)
			if td.units == '3':
				td.density = '%.3f' % round(texel_density*30.48, 3)

			self.report({'INFO'}, "TD is Calculated")

		else:
			self.report({'INFO'}, "No faces selected")

		#Select Objects Again
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.object.mode_set(mode=start_mode)

		return {'FINISHED'}


class Texel_Density_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.texel_density_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		td = context.scene.td

		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_mode = bpy.context.object.mode

		#Get Value for TD Set
		destiny_set_filtered = td.density_set.replace(',', '.')
		try:
			density_new_value = float(destiny_set_filtered)
			if density_new_value < 0.0001:
				density_new_value = 0.0001
		except:
			self.report({'INFO'}, "Density value is wrong")
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='OBJECT')

		for o in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if o.type == 'MESH' and len(o.data.uv_layers) > 0:
				o.select_set(True)
				bpy.context.view_layer.objects.active = o

				#save start selected in 3d view faces
				start_selected_faces = []
				for face_id in range (0, len(o.data.polygons)):
					if bpy.context.active_object.data.polygons[face_id].select == True:
						start_selected_faces.append(face_id)

				bpy.ops.object.mode_set(mode='EDIT')

				#If Set TD from UV Editor sync selection
				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
					utils.Sync_UV_Selection()

				#Select All Polygons if Calculate TD per Object
				if start_mode == 'OBJECT' or td.selected_faces == False:	
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')

				#Get current TD Value from object or faces
				bpy.ops.object.texel_density_check()
				density_current_value = float(td.density)
				if density_current_value < 0.0001:
					density_current_value = 0.0001

				scale_fac = density_new_value/density_current_value
				#check opened image editor window
				ie_area = 0
				flag_exist_area = False
				for area in range(len(bpy.context.screen.areas)):
					if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
						ie_area = area
						flag_exist_area = True
						bpy.context.screen.areas[area].type = 'CONSOLE'
				
				bpy.context.area.type = 'IMAGE_EDITOR'
				
				if bpy.context.area.spaces[0].image != None:
					if bpy.context.area.spaces[0].image.name == 'Render Result':
						bpy.context.area.spaces[0].image = None
				
				if bpy.context.space_data.mode != 'UV':
					bpy.context.space_data.mode = 'UV'
				
				if bpy.context.scene.tool_settings.use_uv_select_sync == False:
					bpy.ops.uv.select_all(action = 'SELECT')
				
				bpy.ops.transform.resize(value=(scale_fac, scale_fac, 1))
				if td.set_method == '0':
					bpy.ops.uv.average_islands_scale()
				bpy.context.area.type = 'VIEW_3D'
				
				if flag_exist_area == True:
					bpy.context.screen.areas[ie_area].type = 'IMAGE_EDITOR'

				bpy.ops.mesh.select_all(action='DESELECT')

				bpy.ops.object.mode_set(mode='OBJECT')
				for face_id in start_selected_faces:
					bpy.context.active_object.data.polygons[face_id].select = True

		#Select Objects Again
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.object.mode_set(mode=start_mode)

		bpy.ops.object.texel_density_check()

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