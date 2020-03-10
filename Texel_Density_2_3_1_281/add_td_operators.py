class Texel_Density_Copy(Operator):
	"""Copy Density"""
	bl_idname = "object.texel_density_copy"
	bl_label = "Copy Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		td = context.scene.td
		
		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_mode = bpy.context.object.mode

		#Calculate TD for Active Object and copy value to Set TD Value Field
		bpy.ops.object.select_all(action='DESELECT')
		start_active_obj.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.object.texel_density_check()
		td.density_set = td.density

		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0) and not x == start_active_obj:
				x.select_set(True)
				bpy.context.view_layer.objects.active = x
				bpy.ops.object.texel_density_set()

		#Select Objects Again
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		
		return {'FINISHED'}


class Calculated_To_Set(Operator):
	"""Copy Calc to Set"""
	bl_idname = "object.calculate_to_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		td = context.scene.td
		
		td.density_set = td.density
		
		return {'FINISHED'}
		

class Preset_Set(Operator):
	"""Preset Set Density"""
	bl_idname = "object.preset_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	TDValue: StringProperty()
	
	def execute(self, context):
		td = context.scene.td
		
		td.density_set = self.TDValue
		bpy.ops.object.texel_density_set()
				
		return {'FINISHED'}
		

class Select_Same_TD(Operator):
	"""Select Faces with same TD"""
	bl_idname = "object.select_same_texel"
	bl_label = "Select Faces with same TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		td = context.scene.td
		
		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_selected_faces_mode = td.selected_faces

		#select mode faces and set "Selected faces" for TD Operations
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		td.selected_faces = True

		#Calculate TD for search
		bpy.ops.object.texel_density_check()
		search_td_value = float(td.density)

		threshold_filtered = td.select_td_threshold.replace(',', '.')
		try:
			threshold_td_value = float(threshold_filtered)
		except:
			threshold_td_value = 0.1
			td.select_td_threshold = "0.1"

		bpy.ops.object.mode_set(mode='OBJECT')
		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0):
				x.select_set(True)
				bpy.context.view_layer.objects.active = x
				face_count = len(bpy.context.active_object.data.polygons)
				
				searched_faces=[]

				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
					#save start selected in 3d view faces
					start_selected_faces = []
					for id in range (0, face_count):
						if bpy.context.active_object.data.polygons[id].select == True:
							start_selected_faces.append(id)
					bpy.ops.object.mode_set(mode='EDIT')

					td_for_all_faces = []
					td_for_all_faces = Calculate_TD_To_List()

					for faceid in start_selected_faces:
						mesh = bpy.context.active_object.data
						bm_local = bmesh.from_edit_mesh(mesh)
						bm_local.faces.ensure_lookup_table()
						uv_layer = bm_local.loops.layers.uv.active
						
						for uvid in range(0, len(bm_local.faces)):
							for loop in bm_local.faces[uvid].loops:
								loop[uv_layer].select = False
						
						for loop in bm_local.faces[faceid].loops:
							loop[uv_layer].select = True
						
						current_poly_td_value = float(td_for_all_faces[faceid])
						if (current_poly_td_value > (search_td_value - threshold_td_value)) and (current_poly_td_value < (search_td_value + threshold_td_value)):
							searched_faces.append(faceid)
					
					mesh = bpy.context.active_object.data
					bm_local = bmesh.from_edit_mesh(mesh)
					bm_local.faces.ensure_lookup_table()
					uv_layer = bm_local.loops.layers.uv.active
					
					for uvid in range(0, len(bm_local.faces)):
						for loop in bm_local.faces[uvid].loops:
							loop[uv_layer].select = False

					for faceid in searched_faces:
						for loop in bm_local.faces[faceid].loops:
							loop[uv_layer].select = True

					bpy.ops.object.mode_set(mode='OBJECT')
					for id in start_selected_faces:
						bpy.context.active_object.data.polygons[id].select = True
				
				else:
					
					td_for_all_faces = []
					td_for_all_faces = Calculate_TD_To_List()

					for faceid in range(0, face_count):
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.reveal()
						bpy.ops.mesh.select_all(action='DESELECT')
						bpy.ops.object.mode_set(mode='OBJECT')
						bpy.context.active_object.data.polygons[faceid].select = True
						bpy.ops.object.mode_set(mode='EDIT')
						current_poly_td_value = float(td_for_all_faces[faceid])
						if (current_poly_td_value > (search_td_value - threshold_td_value)) and (current_poly_td_value < (search_td_value + threshold_td_value)):
							searched_faces.append(faceid)

					bpy.ops.object.mode_set(mode='OBJECT')
					for id in range(0, face_count):
						bpy.context.active_object.data.polygons[id].select = False

					for id in searched_faces:
						bpy.context.active_object.data.polygons[id].select = True

		#Select Objects Again
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		td.selected_faces = start_selected_faces_mode

		bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}