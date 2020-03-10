def draw_callback_px(self, context):
	td = bpy.context.scene.td
	"""Draw on the viewports"""
	#drawing routine
	#Get Parameters
	region = bpy.context.region
	screenTexelX = 2/region.width
	screenTexelY = 2/region.height

	fontSize = 12
	offsetX = int(bpy.context.preferences.addons[__name__].preferences.offsetX)
	offsetY = int(bpy.context.preferences.addons[__name__].preferences.offsetY)
	anchorPos = bpy.context.preferences.addons[__name__].preferences.anchorPos
	font_id = 0
	blf.size(font_id, fontSize, 72)
	blf.color(font_id, 1, 1, 1, 1)

	bake_vc_min_td = float(td.bake_vc_min_td)
	bake_vc_max_td = float(td.bake_vc_max_td)

	#Calculate Text Position from Anchor
	if anchorPos == 'LEFT_BOTTOM':
		fontStartPosX = 0 + offsetX
		fontStartPosY = 0 + offsetY
	elif anchorPos == 'LEFT_TOP':
		fontStartPosX = 0 + offsetX
		fontStartPosY = region.height - offsetY - 15
	elif anchorPos == 'RIGHT_BOTTOM':
		fontStartPosX = region.width - offsetX - 250
		fontStartPosY = 0 + offsetY
	else:
		fontStartPosX = region.width - offsetX - 250
		fontStartPosY = region.height - offsetY - 15

	#Draw TD Values in Viewport via BLF
	blf.position(font_id, fontStartPosX, fontStartPosY + 18, 0)
	blf.draw(font_id, str(round(bake_vc_min_td, 3)))

	blf.position(font_id, fontStartPosX + 115, fontStartPosY + 18, 0)
	blf.draw(font_id, str(round((bake_vc_max_td - bake_vc_min_td) * 0.5 + bake_vc_min_td, 3)))

	blf.position(font_id, fontStartPosX + 240, fontStartPosY + 18, 0)
	blf.draw(font_id, str(round(bake_vc_max_td, 3)))

	blf.position(font_id, fontStartPosX + 52, fontStartPosY - 15, 0)
	blf.draw(font_id, str(round((bake_vc_max_td - bake_vc_min_td) * 0.25 + bake_vc_min_td, 3)))

	blf.position(font_id, fontStartPosX + 177, fontStartPosY - 15, 0)
	blf.draw(font_id, str(round((bake_vc_max_td - bake_vc_min_td) * 0.75 + bake_vc_min_td, 3)))

	#Draw Gradient via shader
	vertex_shader = '''
	in vec2 position;
	out vec3 pos;

	void main()
	{
		pos = vec3(position, 0.0f);
		gl_Position = vec4(position, 0.0f, 1.0f);
	}
	'''

	fragment_shader = '''
	uniform float posXMin;
	uniform float posXMax;

	in vec3 pos;

	void main()
	{
		vec4 b = vec4(0.0f, 0.0f, 1.0f, 1.0f);
		vec4 c = vec4(0.0f, 1.0f, 1.0f, 1.0f);
		vec4 g = vec4(0.0f, 1.0f, 0.0f, 1.0f);
		vec4 y = vec4(1.0f, 1.0f, 0.0f, 1.0f);
		vec4 r = vec4(1.0f, 0.0f, 0.0f, 1.0f);

		float posX25 = (posXMax - posXMin) * 0.25 + posXMin;
		float posX50 = (posXMax - posXMin) * 0.5 + posXMin;
		float posX75 = (posXMax - posXMin) * 0.75 + posXMin;

		float blendColor1 = (pos.x - posXMin)/(posX25 - posXMin);
		float blendColor2 = (pos.x - posX25)/(posX50 - posX25);
		float blendColor3 = (pos.x - posX50)/(posX75 - posX50);
		float blendColor4 = (pos.x - posX75)/(posXMax - posX75);

		gl_FragColor = (c * blendColor1 + b * (1 - blendColor1)) * step(pos.x, posX25) +
						(g * blendColor2 + c * (1 - blendColor2)) * step(pos.x, posX50) * step(posX25, pos.x) +
						(y * blendColor3 + g * (1 - blendColor3)) * step(pos.x, posX75) * step(posX50, pos.x) +
						(r * blendColor4 + y * (1 - blendColor4)) * step(pos.x, posXMax) * step(posX75, pos.x);
	}
	'''

	gradientXMin = screenTexelX * offsetX
	gradientXMax = screenTexelX * (offsetX + 250)
	gradientYMin = screenTexelY * offsetY
	gradientYMax = screenTexelY * (offsetY + 15)

	if anchorPos == 'LEFT_BOTTOM':
		vertices = (
			(-1.0 + gradientXMin, -1.0 + gradientYMax), (-1.0 + gradientXMax, -1.0 + gradientYMax),
			(-1.0 + gradientXMin, -1.0 + gradientYMin), (-1.0 + gradientXMax, -1.0 + gradientYMin))
		posXMin = -1.0 + gradientXMin
		posXMax = -1.0 + gradientXMax
	elif anchorPos == 'LEFT_TOP':
		vertices = (
			(-1.0 + gradientXMin, 1.0 - gradientYMax), (-1.0 + gradientXMax, 1.0 - gradientYMax),
			(-1.0 + gradientXMin, 1.0 - gradientYMin), (-1.0 + gradientXMax, 1.0 - gradientYMin))
		posXMin = -1.0 + gradientXMin
		posXMax = -1.0 +gradientXMax
	elif anchorPos == 'RIGHT_BOTTOM':
		vertices = (
			(1.0 - gradientXMin, -1.0 + gradientYMax), (1.0 - gradientXMax, -1.0 + gradientYMax),
			(1.0 - gradientXMin, -1.0 + gradientYMin), (1.0 - gradientXMax, -1.0 + gradientYMin))
		posXMin = 1.0 - gradientXMax
		posXMax = 1.0 - gradientXMin
	else:
		vertices = (
			(1.0 - gradientXMin, 1.0 - gradientYMax), (1.0 - gradientXMax, 1.0 - gradientYMax),
			(1.0 - gradientXMin, 1.0 - gradientYMin), (1.0 - gradientXMax, 1.0 - gradientYMin))
		posXMin = 1.0 - gradientXMax
		posXMax = 1.0 - gradientXMin


	indices = (
    (0, 1, 2), (2, 1, 3))

	shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
	batch = batch_for_shader(shader, 'TRIS', {"position": vertices}, indices=indices)

	shader.bind()
	shader.uniform_float("posXMin", posXMin)
	shader.uniform_float("posXMax", posXMax)
	batch.draw(shader)


def Calculate_TD_To_List():
	td = bpy.context.scene.td
	calculated_obj_td = []

	#save current mode and active object
	start_active_obj = bpy.context.active_object
	start_mode = bpy.context.object.mode

	#set default values
	Area=0
	gmArea = 0
	textureSizeCurX = 1024
	textureSizeCurY = 1024
	
	#Get texture size from panel
	if td.texture_size == '0':
		textureSizeCurX = 512
		textureSizeCurY = 512
	if td.texture_size == '1':
		textureSizeCurX = 1024
		textureSizeCurY = 1024
	if td.texture_size == '2':
		textureSizeCurX = 2048
		textureSizeCurY = 2048
	if td.texture_size == '3':
		textureSizeCurX = 4096
		textureSizeCurY = 4096
	if td.texture_size == '4':
		try:
			textureSizeCurX = int(td.custom_width)
		except:
			textureSizeCurX = 1024
		try:
			textureSizeCurY = int(td.custom_height)
		except:
			textureSizeCurY = 1024

	if textureSizeCurX < 1 or textureSizeCurY < 1:
		textureSizeCurX = 1024
		textureSizeCurY = 1024

	bpy.ops.object.mode_set(mode='OBJECT')

	face_count = len(bpy.context.active_object.data.polygons)

	#Duplicate and Triangulate Object
	bpy.ops.object.duplicate()
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

	aspectRatio = textureSizeCurX / textureSizeCurY;
	if aspectRatio < 1:
		aspectRatio = 1 / aspectRatio
	largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;

	#get bmesh from active object		
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	bm.faces.ensure_lookup_table()
	
	for x in range(0, face_count):
		Area = 0
		#UV Area calculating
		#get uv-coordinates of verteces of current triangle
		for trisIndex in range(0, len(bm.faces[x].loops) - 2):
			loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
			loopB = bm.faces[x].loops[trisIndex + 1][bm.loops.layers.uv.active].uv
			loopC = bm.faces[x].loops[trisIndex + 2][bm.loops.layers.uv.active].uv
			#get multiplication of vectors of current triangle
			multiVector = Vector2dMultiple(loopA, loopB, loopC)
			#Increment area of current tri to total uv area
			Area += 0.5 * multiVector

		gmArea = bpy.context.active_object.data.polygons[x].area

		#TexelDensity calculating from selected in panel texture size
		if gmArea > 0 and Area > 0:
			texelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length
		else:
			texelDensity = 0.001

		#show calculated values on panel
		if td.units == '0':
			texelDensity = '%.3f' % round(texelDensity, 3)
		if td.units == '1':
			texelDensity = '%.3f' % round(texelDensity*100, 3)
		if td.units == '2':
			texelDensity = '%.3f' % round(texelDensity*2.54, 3)
		if td.units == '3':
			texelDensity = '%.3f' % round(texelDensity*30.48, 3)

		calculated_obj_td.append(float(texelDensity))

	#delete duplicated object
	bpy.ops.object.mode_set(mode='OBJECT')
	
	bpy.ops.object.delete()
	bpy.context.view_layer.objects.active = start_active_obj
	
	bpy.ops.object.mode_set(mode=start_mode)

	return calculated_obj_td


def Show_Gradient(self, context):
	td = context.scene.td
	if td.bake_vc_show_gradient and draw_info["handler"] == None:
			draw_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')
	elif (not td.bake_vc_show_gradient) and (draw_info["handler"] != None):
		bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
		draw_info["handler"] = None


def Saturate(val):
	return max(min(val, 1), 0)


class Checker_Assign(Operator):
	"""Assign Checker Material"""
	bl_idname = "object.checker_assign"
	bl_label = "Assign Checker Material"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		td = context.scene.td

		start_mode = bpy.context.object.mode

		checker_rexolution_x = 1024
		checker_rexolution_y = 1024
		
		#Get texture size from panel
		if td.texture_size == '0':
			checker_rexolution_x = 512
			checker_rexolution_y = 512
		if td.texture_size == '1':
			checker_rexolution_x = 1024
			checker_rexolution_y = 1024
		if td.texture_size == '2':
			checker_rexolution_x = 2048
			checker_rexolution_y = 2048
		if td.texture_size == '3':
			checker_rexolution_x = 4096
			checker_rexolution_y = 4096
		if td.texture_size == '4':
			try:
				checker_rexolution_x = int(td.custom_width)
			except:
				checker_rexolution_x = 1024
			try:
				checker_rexolution_y = int(td.custom_height)
			except:
				checker_rexolution_y = 1024

		if checker_rexolution_x < 1 or checker_rexolution_y < 1:
			checker_rexolution_x = 1024
			checker_rexolution_y = 1024

		#Check exist texture image
		flag_exist_texture = False
		for t in range(len(bpy.data.images)):
			if bpy.data.images[t].name == 'TD_Checker':
				flag_exist_texture = True
				
		# create or not texture
		if flag_exist_texture == False:
			bpy.ops.image.new(name='TD_Checker', width = checker_rexolution_x, height = checker_rexolution_y, generated_type=td.checker_type)
		else:
			bpy.data.images['TD_Checker'].generated_width = checker_rexolution_x
			bpy.data.images['TD_Checker'].generated_height = checker_rexolution_y
			bpy.data.images['TD_Checker'].generated_type=td.checker_type

		#Check exist TD_Checker_mat
		flag_exist_material = False
		for m in range(len(bpy.data.materials)):
			if bpy.data.materials[m].name == 'TD_Checker':
				flag_exist_material = True
				
		# create or not material
		if flag_exist_material == False:
			td_checker_mat = bpy.data.materials.new('TD_Checker')
			td_checker_mat.use_nodes = True
			Nodes = td_checker_mat.node_tree.nodes
			Links = td_checker_mat.node_tree.links
			MixNode = Nodes.new(type="ShaderNodeMixRGB")
			MixNode.location = (-200,200)
			MixNode.blend_type = 'COLOR'
			MixNode.inputs['Fac'].default_value = 1
			Links.new(MixNode.outputs["Color"], Nodes['Principled BSDF'].inputs['Base Color'])

			TexNode = Nodes.new('ShaderNodeTexImage')
			TexNode.location = (-500,300)
			TexNode.image = bpy.data.images['TD_Checker']
			Links.new(TexNode.outputs["Color"], MixNode.inputs['Color1'])

			VcNode = Nodes.new(type="ShaderNodeAttribute")
			VcNode.location = (-500, 0)
			VcNode.attribute_name = "td_vis"
			Links.new(VcNode.outputs["Color"], MixNode.inputs['Color2'])			
		
		bpy.ops.object.mode_set(mode = 'OBJECT')

		if td.checker_method == '1':
			start_active_obj = bpy.context.active_object
			start_selected_obj = bpy.context.selected_objects
			bpy.ops.object.mode_set(mode = 'OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			
			for obj in start_selected_obj:
				if obj.type == 'MESH':
					obj.select_set(True)
					bpy.context.view_layer.objects.active = obj

					#Check save mats on this object or not
					save_this_object = True
					for fm_index in range(len(obj.face_maps)):
						if (obj.face_maps[fm_index].name.startswith('TD_')):
							save_this_object = False

					if save_this_object:
						if len(obj.data.materials) == 0:
							bpy.ops.object.face_map_add()
							obj.face_maps.active.name = 'TD_NoMats'
						elif len(obj.data.materials) > 0:
							bpy.ops.object.mode_set(mode = 'EDIT')
							bpy.ops.mesh.reveal()
							for mat in range(len(obj.data.materials)):
								bpy.ops.mesh.select_all(action='DESELECT')
								bpy.context.object.active_material_index = mat
								bpy.ops.object.material_slot_select()
								bpy.ops.object.face_map_add()
								bpy.ops.object.face_map_assign()
								face_map_composed_name = 'TD_'
								if mat < 10:
									face_map_composed_name += '0'
								face_map_composed_name += str(mat)

								if obj.data.materials[mat] == None:
									face_map_composed_name += 'None'
								else:
									face_map_composed_name += '_' + obj.data.materials[mat].name
								obj.face_maps.active.name = face_map_composed_name
							bpy.ops.object.mode_set(mode = 'OBJECT')


		if td.checker_method == '0':
			for o in bpy.context.selected_objects:
				if o.type == 'MESH' and len(o.data.materials) > 0:
					for q in reversed(range(len(o.data.materials))):
						bpy.context.object.active_material_index = q
						o.data.materials.pop(index = q)

			for o in bpy.context.selected_objects:
				if o.type == 'MESH':
					o.data.materials.append(bpy.data.materials['TD_Checker'])


		if td.checker_method == '1':
			for o in start_selected_obj:
				bpy.ops.object.mode_set(mode = 'OBJECT')
				bpy.ops.object.select_all(action='DESELECT')

				if o.type == 'MESH':
					o.select_set(True)
					bpy.context.view_layer.objects.active = o

					is_assign_td_mat = True
					for q in reversed(range(len(o.data.materials))):
						if obj.active_material != None:
							if obj.active_material.name_full == 'TD_Checker':
								is_assign_td_mat = False

					if is_assign_td_mat:
						o.data.materials.append(bpy.data.materials['TD_Checker'])
						mat_index = len(o.data.materials) - 1
						bpy.ops.object.mode_set(mode = 'EDIT')
						bpy.ops.mesh.reveal()
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.context.object.active_material_index = mat_index
						bpy.ops.object.material_slot_assign()
						bpy.ops.object.mode_set(mode = 'OBJECT')

			for j in start_selected_obj:
				j.select_set(True)
			bpy.context.view_layer.objects.active = start_active_obj

		bpy.ops.object.mode_set(mode = start_mode)
				
		return {'FINISHED'}


class Checker_Restore(Operator):
	"""Restore Saved Materials"""
	bl_idname = "object.checker_restore"
	bl_label = "Restore Saved Materials"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		start_mode = bpy.context.object.mode

		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
				bpy.ops.object.mode_set(mode = 'OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				if obj.type == 'MESH':
					obj.select_set(True)
					bpy.context.view_layer.objects.active = obj
					#Restore Material Assignments and Delete FaceMaps
					if len(obj.face_maps) > 0:
						bpy.ops.object.mode_set(mode = 'EDIT')
						bpy.ops.mesh.reveal()
						for fm_index in reversed(range(len(obj.face_maps))):
							if obj.face_maps[fm_index].name.startswith('TD_'):
								obj.face_maps.active_index = fm_index
								if obj.face_maps[fm_index].name[3:] == 'NoMats':
									bpy.ops.object.face_map_remove()
								else:
									bpy.ops.mesh.select_all(action='DESELECT')
									mat_index_fm = int(obj.face_maps[fm_index].name[3:][:2])
									bpy.context.object.active_material_index = mat_index_fm
									bpy.ops.object.face_map_select()
									bpy.ops.object.material_slot_assign()
									bpy.ops.object.face_map_remove()
						bpy.ops.object.mode_set(mode = 'OBJECT')
						
					#Delete Checker Material
					if len(obj.data.materials) > 0:
						for q in reversed(range(len(obj.data.materials))):
							obj.active_material_index = q
							if obj.active_material != None:
								if obj.active_material.name_full == 'TD_Checker':
									obj.data.materials.pop(index = q)

		bpy.ops.object.select_all(action='DESELECT')
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj

		bpy.ops.object.mode_set(mode = start_mode)

		return {'FINISHED'}


class Clear_Object_List(Operator):
	"""Clear List of stored objects"""
	bl_idname = "object.clear_object_list"
	bl_label = "Clear List of Stored Objects"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_mode = bpy.context.object.mode

		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
				bpy.ops.object.mode_set(mode = 'OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				if obj.type == 'MESH':
					obj.select_set(True)
					bpy.context.view_layer.objects.active = obj
					#Delete FaceMaps
					if len(obj.face_maps) > 0:
						for fm_index in reversed(range(len(obj.face_maps))):
							if obj.face_maps[fm_index].name.startswith('TD_'):
								obj.face_maps.active_index = fm_index
								bpy.ops.object.face_map_remove()

		bpy.ops.object.select_all(action='DESELECT')
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj

		bpy.ops.object.mode_set(mode = start_mode)

		return {'FINISHED'}


class Bake_TD_UV_to_VC(Operator):
	"""Bake Texel Density/UV Islands to Vertex Color"""
	bl_idname = "object.bake_td_uv_to_vc"
	bl_label = "Bake TD to Vertex Color"
	bl_options = {'REGISTER', 'UNDO'}

	mode: StringProperty()
	
	def execute(self, context):
		td = context.scene.td
		
		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_mode = bpy.context.object.mode

		bake_vc_min_td = float(td.bake_vc_min_td)
		bake_vc_max_td = float(td.bake_vc_max_td)
		
		if (bake_vc_min_td == bake_vc_max_td) and self.mode == "TD":
			self.report({'INFO'}, "Value Range is wrong")
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='OBJECT')
		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0):
				x.select_set(True)
				bpy.context.view_layer.objects.active = x
								
				face_count = len(bpy.context.active_object.data.polygons)

				start_selected_faces = []
				if start_mode == "EDIT":
					for f in bpy.context.active_object.data.polygons:
						if f.select:
							start_selected_faces.append(f.index)

				shouldAddVC = True
				for vc in x.data.vertex_colors:
					if vc.name == "td_vis":
						shouldAddVC = False

				if shouldAddVC:
					bpy.ops.mesh.vertex_color_add()
					x.data.vertex_colors.active.name = "td_vis"

				x.data.vertex_colors["td_vis"].active = True

				face_list = []
				if self.mode == "TD":
					face_list = Calculate_TD_To_List()
				if self.mode == "UV":
					face_list = bpy_extras.mesh_utils.mesh_linked_uv_islands(bpy.context.active_object.data)

				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()

				if self.mode == "TD":
					for faceid in range(0, face_count):
						remaped_td = (face_list[faceid] - bake_vc_min_td) / (bake_vc_max_td - bake_vc_min_td)
						remaped_td = Saturate(remaped_td)
						hue = (1 - remaped_td) * 0.67
						color = colorsys.hsv_to_rgb(hue, 1, 1)
						color4 = (color[0], color[1], color[2], 1)
						
						for loop in bm.faces[faceid].loops:
							loop[bm.loops.layers.color.active] = color4

				if self.mode == "UV":
					for uvIsland in face_list:
						randomHue = random.randrange(0, 10, 1)/10
						randomValue = random.randrange(4, 10, 1)/10
						color = colorsys.hsv_to_rgb(randomHue, 1, randomValue)
						color4 = (color[0], color[1], color[2], 1)

						for faceID in uvIsland:
							for loop in bm.faces[faceID].loops:
								loop[bm.loops.layers.color.active] = color4

				bpy.ops.object.mode_set(mode='OBJECT')
					
				if start_mode == "EDIT":
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.object.mode_set(mode='OBJECT')
					for faceid in start_selected_faces:
						bpy.context.active_object.data.polygons[faceid].select = True

		bpy.ops.object.select_all(action='DESELECT')
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.object.mode_set(mode = start_mode)
		bpy.context.space_data.shading.color_type = 'VERTEX'

		Show_Gradient(self, context)

		return {'FINISHED'}


class Clear_TD_VC(Operator):
	"""Clear TD Baked into Vertex Color"""
	bl_idname = "object.clear_td_vc"
	bl_label = "Clear Vertex Color from TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_mode = bpy.context.object.mode

		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
				bpy.ops.object.mode_set(mode = 'OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				if obj.type == 'MESH':
					obj.select_set(True)
					bpy.context.view_layer.objects.active = obj
					#Delete FaceMaps
					if len(obj.data.vertex_colors) > 0:
						for vc in obj.data.vertex_colors:
							if vc.name == "td_vis":
								vc.active = True
								bpy.ops.mesh.vertex_color_remove()

		bpy.ops.object.select_all(action='DESELECT')
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj

		bpy.ops.object.mode_set(mode = start_mode)

		return {'FINISHED'}