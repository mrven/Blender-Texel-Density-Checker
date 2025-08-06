import bpy
import bmesh
import math
import colorsys
import blf
import bgl
import gpu
import random
import bpy_extras.mesh_utils

from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty

from . import utils
from . import props


def Draw_Callback_Px(self, context):
	td = bpy.context.scene.td
	"""Draw on the viewports"""
	#drawing routine
	#Get Parameters
	region = bpy.context.region
	screen_texel_x = 2/region.width
	screen_texel_y = 2/region.height

	font_size = 12
	offset_x = int(bpy.context.preferences.addons[__package__].preferences.offset_x)
	offset_y = int(bpy.context.preferences.addons[__package__].preferences.offset_y)
	anchor_pos = bpy.context.preferences.addons[__package__].preferences.anchor_pos
	font_id = 0
	blf.size(font_id, font_size, 72)
	blf.color(font_id, 1, 1, 1, 1)

	bake_min_value = 0
	bake_max_value = 0
	bake_value_precision = 3

	if td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC":	
		bake_min_value = float(td.bake_vc_min_td)
		bake_max_value = float(td.bake_vc_max_td)

	elif td.bake_vc_mode == "UV_SPACE_TO_VC":
		bake_min_value = float(td.bake_vc_min_space)
		bake_max_value = float(td.bake_vc_max_space)

	if abs(bake_max_value - bake_min_value) <= 3:
		bake_value_precision = 5
	elif abs(bake_max_value - bake_min_value) <= 12:
		bake_value_precision = 4
	elif abs(bake_max_value - bake_min_value) <= 25:
		bake_value_precision = 3
	elif abs(bake_max_value - bake_min_value) <= 50:
		bake_value_precision = 2
	else:
		bake_value_precision = 1


	#Calculate Text Position from Anchor
	if anchor_pos == 'LEFT_BOTTOM':
		font_start_pos_x = 0 + offset_x
		font_start_pos_y = 0 + offset_y
	elif anchor_pos == 'LEFT_TOP':
		font_start_pos_x = 0 + offset_x
		font_start_pos_y = region.height - offset_y - 15
	elif anchor_pos == 'RIGHT_BOTTOM':
		font_start_pos_x = region.width - offset_x - 250
		font_start_pos_y = 0 + offset_y
	else:
		font_start_pos_x = region.width - offset_x - 250
		font_start_pos_y = region.height - offset_y - 15

	#Draw TD Values in Viewport via BLF
	blf.position(font_id, font_start_pos_x, font_start_pos_y + 18, 0)
	blf.draw(font_id, str(round(bake_min_value, bake_value_precision)))

	blf.position(font_id, font_start_pos_x + 115, font_start_pos_y + 18, 0)
	blf.draw(font_id, str(round((bake_max_value - bake_min_value) * 0.5 + bake_min_value, bake_value_precision)))

	blf.position(font_id, font_start_pos_x + 240, font_start_pos_y + 18, 0)
	blf.draw(font_id, str(round(bake_max_value, bake_value_precision)))

	blf.position(font_id, font_start_pos_x + 52, font_start_pos_y - 15, 0)
	blf.draw(font_id, str(round((bake_max_value - bake_min_value) * 0.25 + bake_min_value, bake_value_precision)))

	blf.position(font_id, font_start_pos_x + 177, font_start_pos_y - 15, 0)
	blf.draw(font_id, str(round((bake_max_value - bake_min_value) * 0.75 + bake_min_value, bake_value_precision)))

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
	uniform float pos_x_min;
	uniform float pos_x_max;

	in vec3 pos;

	void main()
	{
		vec4 b = vec4(0.0f, 0.0f, 1.0f, 1.0f);
		vec4 c = vec4(0.0f, 1.0f, 1.0f, 1.0f);
		vec4 g = vec4(0.0f, 1.0f, 0.0f, 1.0f);
		vec4 y = vec4(1.0f, 1.0f, 0.0f, 1.0f);
		vec4 r = vec4(1.0f, 0.0f, 0.0f, 1.0f);

		float pos_x_25 = (pos_x_max - pos_x_min) * 0.25 + pos_x_min;
		float pos_x_50 = (pos_x_max - pos_x_min) * 0.5 + pos_x_min;
		float pos_x_75 = (pos_x_max - pos_x_min) * 0.75 + pos_x_min;

		float blendColor1 = (pos.x - pos_x_min)/(pos_x_25 - pos_x_min);
		float blendColor2 = (pos.x - pos_x_25)/(pos_x_50 - pos_x_25);
		float blendColor3 = (pos.x - pos_x_50)/(pos_x_75 - pos_x_50);
		float blendColor4 = (pos.x - pos_x_75)/(pos_x_max - pos_x_75);

		gl_FragColor = (c * blendColor1 + b * (1 - blendColor1)) * step(pos.x, pos_x_25) +
						(g * blendColor2 + c * (1 - blendColor2)) * step(pos.x, pos_x_50) * step(pos_x_25, pos.x) +
						(y * blendColor3 + g * (1 - blendColor3)) * step(pos.x, pos_x_75) * step(pos_x_50, pos.x) +
						(r * blendColor4 + y * (1 - blendColor4)) * step(pos.x, pos_x_max) * step(pos_x_75, pos.x);
	}
	'''

	gradient_x_min = screen_texel_x * offset_x
	gradient_x_max = screen_texel_x * (offset_x + 250)
	gradient_y_min = screen_texel_y * offset_y
	gradient_y_max = screen_texel_y * (offset_y + 15)

	if anchor_pos == 'LEFT_BOTTOM':
		vertices = (
			(-1.0 + gradient_x_min, -1.0 + gradient_y_max), (-1.0 + gradient_x_max, -1.0 + gradient_y_max),
			(-1.0 + gradient_x_min, -1.0 + gradient_y_min), (-1.0 + gradient_x_max, -1.0 + gradient_y_min))
		pos_x_min = -1.0 + gradient_x_min
		pos_x_max = -1.0 + gradient_x_max
	elif anchor_pos == 'LEFT_TOP':
		vertices = (
			(-1.0 + gradient_x_min, 1.0 - gradient_y_max), (-1.0 + gradient_x_max, 1.0 - gradient_y_max),
			(-1.0 + gradient_x_min, 1.0 - gradient_y_min), (-1.0 + gradient_x_max, 1.0 - gradient_y_min))
		pos_x_min = -1.0 + gradient_x_min
		pos_x_max = -1.0 +gradient_x_max
	elif anchor_pos == 'RIGHT_BOTTOM':
		vertices = (
			(1.0 - gradient_x_min, -1.0 + gradient_y_max), (1.0 - gradient_x_max, -1.0 + gradient_y_max),
			(1.0 - gradient_x_min, -1.0 + gradient_y_min), (1.0 - gradient_x_max, -1.0 + gradient_y_min))
		pos_x_min = 1.0 - gradient_x_max
		pos_x_max = 1.0 - gradient_x_min
	else:
		vertices = (
			(1.0 - gradient_x_min, 1.0 - gradient_y_max), (1.0 - gradient_x_max, 1.0 - gradient_y_max),
			(1.0 - gradient_x_min, 1.0 - gradient_y_min), (1.0 - gradient_x_max, 1.0 - gradient_y_min))
		pos_x_min = 1.0 - gradient_x_max
		pos_x_max = 1.0 - gradient_x_min


	indices = (
    (0, 1, 2), (2, 1, 3))

	shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
	batch = batch_for_shader(shader, 'TRIS', {"position": vertices}, indices=indices)

	shader.bind()
	shader.uniform_float("pos_x_min", pos_x_min)
	shader.uniform_float("pos_x_max", pos_x_max)
	batch.draw(shader)


class Checker_Assign(bpy.types.Operator):
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
			nodes = td_checker_mat.node_tree.nodes
			links = td_checker_mat.node_tree.links
			mix_node = nodes.new(type="ShaderNodeMixRGB")
			mix_node.location = (-200,200)
			mix_node.blend_type = 'COLOR'
			mix_node.inputs['Fac'].default_value = 1
			links.new(mix_node.outputs["Color"], nodes['Principled BSDF'].inputs['Base Color'])

			tex_node = nodes.new('ShaderNodeTexImage')
			tex_node.location = (-500,300)
			tex_node.image = bpy.data.images['TD_Checker']
			links.new(tex_node.outputs["Color"], mix_node.inputs['Color1'])

			vc_node = nodes.new(type="ShaderNodeAttribute")
			vc_node.location = (-500, 0)
			vc_node.attribute_name = "td_vis"
			links.new(vc_node.outputs["Color"], mix_node.inputs['Color2'])

			mapper_node = nodes.new(type="ShaderNodeMapping")
			mapper_node.location = (-800, 300)
			mapper_node.inputs['Scale'].default_value[0] = float(td.checker_uv_scale)
			mapper_node.inputs['Scale'].default_value[1] = float(td.checker_uv_scale)
			links.new(mapper_node.outputs["Vector"], tex_node.inputs['Vector'])
			
			uv_node = nodes.new(type="ShaderNodeUVMap")
			uv_node.location = (-1000, 220)
			links.new(uv_node.outputs["UV"], mapper_node.inputs['Vector'])

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
									face_map_composed_name += '_None'
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


class Checker_Restore(bpy.types.Operator):
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


class Clear_Checker_Face_Maps(bpy.types.Operator):
	"""Clear Stored Checker Face Maps"""
	bl_idname = "object.clear_checker_face_maps"
	bl_label = "Clear Stored Checker Face Maps"
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


class Bake_TD_UV_to_VC(bpy.types.Operator):
	"""Bake Texel Density/UV Islands to Vertex Color"""
	bl_idname = "object.bake_td_uv_to_vc"
	bl_label = "Bake TD to Vertex Color"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		td = context.scene.td
		
		#save current mode and active object
		start_active_obj = bpy.context.active_object
		start_selected_obj = bpy.context.selected_objects
		start_mode = bpy.context.object.mode

		bake_vc_min_td = float(td.bake_vc_min_td)
		bake_vc_max_td = float(td.bake_vc_max_td)
		bake_vc_min_space = float(td.bake_vc_min_space)
		bake_vc_max_space = float(td.bake_vc_max_space)

		if (bake_vc_min_td == bake_vc_max_td) and (td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC"):
			self.report({'INFO'}, "Value Range is wrong")
			return {'CANCELLED'}

		if (bake_vc_min_space == bake_vc_max_space) and td.bake_vc_mode == "UV_SPACE_TO_VC":
			self.report({'INFO'}, "Value Range is wrong")
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='OBJECT')
		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if (x.type == 'MESH' and len(x.data.uv_layers) > 0 and len(x.data.polygons) > 0):
				x.select_set(True)
				bpy.context.view_layer.objects.active = x
								
				face_count = len(bpy.context.active_object.data.polygons)

				start_selected_faces = []
				if start_mode == "EDIT":
					for f in bpy.context.active_object.data.polygons:
						if f.select:
							start_selected_faces.append(f.index)

				should_add_vc = True
				for vc in x.data.vertex_colors:
					if vc.name == "td_vis":
						should_add_vc = False

				if should_add_vc:
					bpy.ops.mesh.vertex_color_add()
					x.data.vertex_colors.active.name = "td_vis"

				x.data.vertex_colors["td_vis"].active = True

				islands_list = []
				face_td_area_list = []

				
				if td.bake_vc_mode == "UV_ISLANDS_TO_VC" and td.uv_islands_to_vc_mode == "OVERLAP":
					islands_list = bpy_extras.mesh_utils.mesh_linked_uv_islands(bpy.context.active_object.data)
				else:
					islands_list = utils.Get_UV_Islands()
				
				face_td_area_list = utils.Calculate_TD_Area_To_List()

				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()

				if td.bake_vc_mode == "TD_FACES_TO_VC":
					for face_id in range(0, face_count):
						color = utils.Value_To_Color(face_td_area_list[face_id][0], bake_vc_min_td, bake_vc_max_td)

						for loop in bm.faces[face_id].loops:
							loop[bm.loops.layers.color.active] = color

				elif td.bake_vc_mode == "UV_ISLANDS_TO_VC":
					for uv_island in islands_list:
						random_hue = random.randrange(0, 10, 1)/10
						random_value = random.randrange(2, 10, 1)/10
						random_saturation = random.randrange(7, 10, 1)/10
						color = colorsys.hsv_to_rgb(random_hue, random_saturation, random_value)
						color4 = (color[0], color[1], color[2], 1)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.active] = color4

				elif td.bake_vc_mode == "UV_SPACE_TO_VC":
					for uv_island in islands_list:
						island_area = 0
						for face_id in uv_island:						
							island_area += face_td_area_list[face_id][1]
						
						island_area *= 100

						color = utils.Value_To_Color(island_area, bake_vc_min_space, bake_vc_max_space)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.active] = color

				elif td.bake_vc_mode == "TD_ISLANDS_TO_VC":
					for uv_island in islands_list:
						island_td = 0
						island_area = 0
						#Calculate Total Island Area
						for face_id in uv_island:
							island_area += face_td_area_list[face_id][1]

						if island_area == 0:
							island_area = 0.000001

						for face_id in uv_island:						
							island_td += face_td_area_list[face_id][0] * face_td_area_list[face_id][1]/island_area

						color = utils.Value_To_Color(island_td, bake_vc_min_td, bake_vc_max_td)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.active] = color
				
				bpy.ops.object.mode_set(mode='OBJECT')
					
				if start_mode == "EDIT":
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.object.mode_set(mode='OBJECT')
					for face_id in start_selected_faces:
						bpy.context.active_object.data.polygons[face_id].select = True

		bpy.ops.object.select_all(action='DESELECT')
		for x in start_selected_obj:
			x.select_set(True)
		bpy.context.view_layer.objects.active = start_active_obj
		bpy.ops.object.mode_set(mode = start_mode)
		bpy.context.space_data.shading.color_type = 'VERTEX'

		if td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC" or td.bake_vc_mode == "UV_SPACE_TO_VC":
			props.Show_Gradient(self, context)

		return {'FINISHED'}


class Clear_TD_VC(bpy.types.Operator):
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


classes = (
    Checker_Assign,
	Checker_Restore,
	Clear_Checker_Face_Maps,
	Bake_TD_UV_to_VC,
	Clear_TD_VC,
)	


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)