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
from datetime import datetime

from . import utils
from . import props


# Draw Reference Gradient Line for Color Visualizer
def Draw_Callback_Px(self, context):
	td = bpy.context.scene.td
	"""Draw on the viewports"""

	# Get Parameters
	region = bpy.context.region
	screen_texel_x = 2 / region.width  # 2 because Screen Space -1.0 to 1.0
	screen_texel_y = 2 / region.height

	font_size = 12
	offset_x = int(bpy.context.preferences.addons[__package__].preferences.offset_x)
	offset_y = int(bpy.context.preferences.addons[__package__].preferences.offset_y)
	anchor_pos = bpy.context.preferences.addons[__package__].preferences.anchor_pos
	font_id = 0
	blf.size(font_id, font_size)
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

	elif td.bake_vc_mode == 'DISTORTION':
		# Calculate Min/Max for range
		bake_min_value = 100 - float(td.bake_vc_distortion_range)
		if bake_min_value < 0:
			bake_min_value = 0
		bake_max_value = 100 + float(td.bake_vc_distortion_range)

	# Number of Symbols after Point for TD Values for Gradient
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

	# Calculate Text Position from Anchor.
	# Anchor and offset set in Preferences
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

	# Draw TD Values (Text) in Viewport via BLF
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

	# Draw Gradient Line via Shader
	vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
	vert_out.smooth('VEC3', "pos")

	shader_info = gpu.types.GPUShaderCreateInfo()
	shader_info.push_constant('FLOAT', "pos_x_min")
	shader_info.push_constant('FLOAT', "pos_x_max")
	shader_info.vertex_in(0, 'VEC2', "position")
	shader_info.vertex_out(vert_out)
	shader_info.fragment_out(0, 'VEC4', "FragColor")

	shader_info.vertex_source('''
	//in vec2 position;
	//out vec3 pos;

	void main()
	{
		pos = vec3(position, 0.0f);
		gl_Position = vec4(position, 0.0f, 1.0f);
	}
	''')

	fshader_src = '''
	//uniform float pos_x_min;
	//uniform float pos_x_max;

	//in vec3 pos;
	'''
	if td.bake_vc_colorization == "TD_COLORIZE_HUE":
		fshader_src += '''
	void main()
	{
		// Pure Colors
		vec4 b = vec4(0.0f, 0.0f, 1.0f, 1.0f);	// Blue	0%
		vec4 c = vec4(0.0f, 1.0f, 1.0f, 1.0f);	// Cyan	25%
		vec4 g = vec4(0.0f, 1.0f, 0.0f, 1.0f);	// Green	50%
		vec4 y = vec4(1.0f, 1.0f, 0.0f, 1.0f);	// Yellow	75%
		vec4 r = vec4(1.0f, 0.0f, 0.0f, 1.0f);	// Red	100%

		// Screen Space Coordinates for Intermediate Pure Colors
		float pos_x_25 = (pos_x_max - pos_x_min) * 0.25 + pos_x_min;
		float pos_x_50 = (pos_x_max - pos_x_min) * 0.5 + pos_x_min;
		float pos_x_75 = (pos_x_max - pos_x_min) * 0.75 + pos_x_min;

		// Intermediate Blend Values (0% - 25% => 0 - 1, 25% - 50% => 0 - 1, etc.)
		float blendColor1 = (pos.x - pos_x_min)/(pos_x_25 - pos_x_min);
		float blendColor2 = (pos.x - pos_x_25)/(pos_x_50 - pos_x_25);
		float blendColor3 = (pos.x - pos_x_50)/(pos_x_75 - pos_x_50);
		float blendColor4 = (pos.x - pos_x_75)/(pos_x_max - pos_x_75);

		// Calculate Final Colors - Pure Colors and Blends between them 
		FragColor = (c * blendColor1 + b * (1 - blendColor1)) * step(pos.x, pos_x_25) +
						(g * blendColor2 + c * (1 - blendColor2)) * step(pos.x, pos_x_50) * step(pos_x_25, pos.x) +
						(y * blendColor3 + g * (1 - blendColor3)) * step(pos.x, pos_x_75) * step(pos_x_50, pos.x) +
						(r * blendColor4 + y * (1 - blendColor4)) * step(pos.x, pos_x_max) * step(pos_x_75, pos.x);
	}
		'''
	elif td.bake_vc_colorization == "TD_COLORIZE_GRAYSCALE_LINEAR":
		fshader_src += '''
	void main()
	{
		float pos_x_normalized = (pos.x - pos_x_min) / (pos_x_max - pos_x_min);
		FragColor = vec4(pos_x_normalized, pos_x_normalized, pos_x_normalized, 1.0f);
	}
		'''
	elif td.bake_vc_colorization == "TD_COLORIZE_GRAYSCALE_SQRT":
		fshader_src += '''
	void main()
	{
		float pos_x_normalized = sqrt((pos.x - pos_x_min) / (pos_x_max - pos_x_min));
		FragColor = vec4(pos_x_normalized, pos_x_normalized, pos_x_normalized, 1.0f);
	}
		'''
	else:
		#FUTURE: elif and attach F shader for more colorization?
		fshader_src += '''
	void main()
	{
		FragColor = vec4(1.0f, 0.0f, 1.0f, 1.0f);
	}
		'''
	shader_info.fragment_source(fshader_src)

	# Gradient Bounds with range 0.0 - 2.0
	gradient_x_min = screen_texel_x * offset_x
	gradient_x_max = screen_texel_x * (offset_x + 250)  # 250 is width of gradient line TODO:Move to constant var
	gradient_y_min = screen_texel_y * offset_y
	gradient_y_max = screen_texel_y * (offset_y + 15)  # 15 is height of gradient line	TODO:Move to constant var

	# Calculate vertices coordinates relative from the anchor
	# And X Min/Max in Screen Space (-1.0 - 1.0). It's Transferring to shader
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
		pos_x_max = -1.0 + gradient_x_max
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

	# Set Shader Parameters and Draw
	indices = ((0, 1, 2), (2, 1, 3))

	shader = gpu.shader.create_from_info(shader_info)
	del vert_out
	del shader_info

	batch = batch_for_shader(shader, 'TRIS', {"position": vertices}, indices=indices)

	shader.bind()
	shader.uniform_float("pos_x_min", pos_x_min)
	shader.uniform_float("pos_x_max", pos_x_max)
	batch.draw(shader)


# Assign of Checker Material
class Checker_Assign(bpy.types.Operator):
	"""Assign Checker Material"""
	bl_idname = "object.checker_assign"
	bl_label = "Assign Checker Material"
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

		# Get texture size from panel
		checker_resolution_x = 1024
		checker_resolution_y = 1024

		if td.texture_size != 'CUSTOM':
			checker_resolution_x = checker_resolution_y = int(td.texture_size)
		else:
			try:
				checker_resolution_x = int(td.custom_width)
			except:
				checker_resolution_x = 1024
			try:
				checker_resolution_y = int(td.custom_height)
			except:
				checker_resolution_y = 1024

		if checker_resolution_x < 1 or checker_resolution_y < 1:
			checker_resolution_x = 1024
			checker_resolution_y = 1024

		# Check exist texture image
		td_checker_texture = None
		for tex in bpy.data.images:
			if tex.is_td_texture:
				td_checker_texture = tex

		# Create Checker Texture (if not Exist yet) with parameters from Panel
		if not td_checker_texture:
			td_checker_texture = bpy.data.images.new(name='TD_Checker', width=checker_resolution_x, height=checker_resolution_y)
			td_checker_texture.generated_type=td.checker_type
			td_checker_texture.is_td_texture = True
		else:
			td_checker_texture.generated_width = checker_resolution_x
			td_checker_texture.generated_height = checker_resolution_y
			td_checker_texture.generated_type = td.checker_type

		# Check exist TD_Checker_mat
		td_checker_material = None
		for mat in bpy.data.materials:
			if mat.is_td_material:
				td_checker_material = mat

		# Create material (if not Exist yet) and Setup nodes
		if not td_checker_material:
			td_checker_material = bpy.data.materials.new('TD_Checker')
			td_checker_material.is_td_material = True
			td_checker_material.use_nodes = True
			nodes = td_checker_material.node_tree.nodes
			links = td_checker_material.node_tree.links
			# Color Mix Node for Blending Checker Texture with VC
			mix_node = nodes.new(type="ShaderNodeMixRGB")
			mix_node.location = (-200, 200)
			mix_node.blend_type = 'COLOR'
			mix_node.inputs['Fac'].default_value = 1
			links.new(mix_node.outputs["Color"], nodes['Principled BSDF'].inputs['Base Color'])
			# Get Checker Texture
			tex_node = nodes.new('ShaderNodeTexImage')
			tex_node.location = (-500, 300)
			tex_node.image = td_checker_texture
			tex_node.interpolation = 'Closest'
			links.new(tex_node.outputs["Color"], mix_node.inputs['Color1'])
			# Get VC with baked TD
			vc_node = nodes.new(type="ShaderNodeAttribute")
			vc_node.location = (-500, 0)
			vc_node.attribute_name = "td_vis"
			links.new(vc_node.outputs["Color"], mix_node.inputs['Color2'])
			# UV Mapping for Checker Texture
			mapper_node = nodes.new(type="ShaderNodeMapping")
			mapper_node.location = (-800, 300)
			# Scale of UV Mapping sets from Panel (UV Scale)
			mapper_node.inputs['Scale'].default_value[0] = float(td.checker_uv_scale)
			mapper_node.inputs['Scale'].default_value[1] = float(td.checker_uv_scale)
			links.new(mapper_node.outputs["Vector"], tex_node.inputs['Vector'])
			uv_node = nodes.new(type="ShaderNodeUVMap")
			uv_node.location = (-1000, 220)
			links.new(uv_node.outputs["UV"], mapper_node.inputs['Vector'])

		bpy.ops.object.mode_set(mode='OBJECT')

		# Store Real Materials and Replace to Checker Material
		if td.checker_method == 'STORE':
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')

			for obj in start_selected_obj:
				if obj.type == 'MESH':
					bpy.context.view_layer.objects.active = obj
					bpy.context.view_layer.objects.active.select_set(True)

					# Check save mats on this object or not
					save_this_object = True

					# td_settings is Custom Property per Object
					# for saving Real Materials Assignment (Index, Mat Slot)
					if len(obj.td_settings) > 0:
						save_this_object = False

					# Save Real Materials Assignment
					if save_this_object:
						if len(obj.data.materials) > 0:
							bpy.ops.object.mode_set(mode='OBJECT')
							face_count = len(bpy.context.active_object.data.polygons)
							bpy.ops.object.mode_set(mode='EDIT')
							bm = bmesh.from_edit_mesh(obj.data)
							bm.faces.ensure_lookup_table()

							for face_id in range(face_count):
								obj.td_settings.add()
								obj.td_settings[len(obj.td_settings) - 1].TriIndex = face_id
								obj.td_settings[len(obj.td_settings) - 1].MatIndex = bm.faces[face_id].material_index

							bpy.ops.object.mode_set(mode='OBJECT')

		# Destroy Real Materials Slots and Assign Checker Material
		if td.checker_method == 'REPLACE':
			for o in start_selected_obj:
				if o.type == 'MESH' and len(o.data.materials) > 0:
					for q in reversed(range(len(o.data.materials))):
						bpy.context.object.active_material_index = q
						o.data.materials.pop(index=q)

			for o in start_selected_obj:
				if o.type == 'MESH':
					o.data.materials.append(td_checker_material)

		# If Store and Replace Method
		if td.checker_method == 'STORE':
			for o in start_selected_obj:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')

				if o.type == 'MESH':
					bpy.context.view_layer.objects.active = o
					bpy.context.view_layer.objects.active.select_set(True)

					# Check object already has slot with Checker Material
					is_assign_td_mat = True
					for q in reversed(range(len(o.data.materials))):
						if o.active_material is not None:
							if o.active_material.is_td_material:
								is_assign_td_mat = False

					# Added New Material Slot for Checker Material and Assign him to all faces
					if is_assign_td_mat:
						o.data.materials.append(td_checker_material)
						mat_index = len(o.data.materials) - 1
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.reveal()
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.context.object.active_material_index = mat_index
						bpy.ops.object.material_slot_assign()
						bpy.ops.object.mode_set(mode='OBJECT')

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.Print_Execution_Time("Assign of Checker Material", start_time)
		return {'FINISHED'}


# Restore Real Materials
class Checker_Restore(bpy.types.Operator):
	"""Restore Saved Materials"""
	bl_idname = "object.checker_restore"
	bl_label = "Restore Saved Materials"
	bl_options = {'REGISTER'}

	def execute(self, context):
		start_time = datetime.now()
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')

			if obj.type == 'MESH':
				bpy.context.view_layer.objects.active = obj
				bpy.context.view_layer.objects.active.select_set(True)
				face_count = len(bpy.context.active_object.data.polygons)
				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(obj.data)
				bm.faces.ensure_lookup_table()
				# Read and Apply Saved pairs (face, material index) from custom property td_settings
				if len(obj.td_settings) > 0:
					for face_id in range(face_count):
						bm.faces[face_id].material_index = obj.td_settings[face_id].MatIndex
				bpy.ops.object.mode_set(mode='OBJECT')
				# Delete all saved pairs
				obj.td_settings.clear()

				# Delete Checker Material from object
				if len(obj.data.materials) > 0:
					for q in reversed(range(len(obj.data.materials))):
						obj.active_material_index = q
						if obj.active_material is not None:
							if obj.active_material.is_td_material:
								obj.data.materials.pop(index=q)

		bpy.ops.object.select_all(action='DESELECT')
		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.Print_Execution_Time("Restore Materials", start_time)
		return {'FINISHED'}


# Clear Saved Real Materials assignment from Objects
class Clear_Saved_Materials(bpy.types.Operator):
	"""Clear Stored Materials"""
	bl_idname = "object.clear_checker_materials"
	bl_label = "Clear Stored Materials"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			if obj.type == 'MESH':
				bpy.context.view_layer.objects.active = obj
				bpy.context.view_layer.objects.active.select_set(True)
				# Delete pairs (face, material slot index)
				if len(obj.td_settings) > 0:
					obj.td_settings.clear()

		bpy.ops.object.select_all(action='DESELECT')
		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.Print_Execution_Time("Clear Saved Materials", start_time)
		return {'FINISHED'}


# Bake TD to VC
class Bake_TD_UV_to_VC(bpy.types.Operator):
	"""Bake Texel Density/UV Islands to Vertex Color"""
	bl_idname = "object.bake_td_uv_to_vc"
	bl_label = "Bake TD to Vertex Color"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td

		# Determine the colorization method to use:
		if td.bake_vc_colorization == "TD_COLORIZE_HUE":
			colorize = utils.Value_To_Color
		elif td.bake_vc_colorization == "TD_COLORIZE_GRAYSCALE_LINEAR":
			colorize = utils.Value_To_Grayscale_Linear
		elif td.bake_vc_colorization == "TD_COLORIZE_GRAYSCALE_SQRT":
			colorize = utils.Value_To_Grayscale_Sqrt
		elif td.bake_vc_colorization == "TD_COLORIZE_FIXED24_RGB8":
			colorize = utils.Value_To_Fixed24
		else:
			self.report({'ERROR'}, "Invalid VC colorization method \"%s\"" % td.bake_vc_colorization)
			return {'CANCELLED'}

		# Save current mode and active object
		start_active_obj = bpy.context.active_object
		start_mode = bpy.context.object.mode
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		# Range for baking TD
		bake_vc_min_td = float(td.bake_vc_min_td)
		bake_vc_max_td = float(td.bake_vc_max_td)
		# Range for baking UV Space
		bake_vc_min_space = float(td.bake_vc_min_space)
		bake_vc_max_space = float(td.bake_vc_max_space)

		# Range for baking UV Distortion
		bake_vc_distortion_range = float(td.bake_vc_distortion_range)

		bpy.ops.object.mode_set(mode='OBJECT')

		# Automatic Min/Max TD
		if td.bake_vc_auto_min_max and (td.bake_vc_mode == 'TD_FACES_TO_VC' or td.bake_vc_mode == 'TD_ISLANDS_TO_VC'):
			td_area_list = []
			for x in start_selected_obj:
				bpy.ops.object.select_all(action='DESELECT')
				if x.type == 'MESH' and len(x.data.uv_layers) > 0 and len(x.data.polygons) > 0:
					bpy.context.view_layer.objects.active = x
					bpy.context.view_layer.objects.active.select_set(True)

					td_area_list.append(utils.Calculate_TD_Area_To_List_CPP())

			# Found Min and Max TD
			if len(td_area_list) > 0:
				min_calculated_td = 9999999
				max_calculated_td = 0
				for obj_td_list in td_area_list:
					for index in range(0, int(len(obj_td_list) / 2)):
						if obj_td_list[index * 2] < min_calculated_td:
							min_calculated_td = obj_td_list[index * 2]
						if obj_td_list[index * 2] > max_calculated_td:
							max_calculated_td = obj_td_list[index * 2]

				bake_vc_min_td = min_calculated_td
				bake_vc_max_td = max_calculated_td

				td.bake_vc_min_td = '%.3f' % round(min_calculated_td, 3)
				td.bake_vc_max_td = '%.3f' % round(max_calculated_td, 3)

		for x in start_selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			if x.type == 'MESH' and len(x.data.uv_layers) > 0 and len(x.data.polygons) > 0:
				bpy.context.view_layer.objects.active = x
				bpy.context.view_layer.objects.active.select_set(True)

				face_count = len(bpy.context.active_object.data.polygons)

				# Save selected faces
				start_selected_faces = []
				if start_mode == "EDIT":
					for f in bpy.context.active_object.data.polygons:
						if f.select:
							start_selected_faces.append(f.index)

				# Add vertex color group for visualization over material
				should_add_vc = True
				for vc in x.data.vertex_colors:
					if vc.name == "td_vis":
						should_add_vc = False

				if should_add_vc:
					bpy.ops.geometry.color_attribute_add(domain='CORNER', data_type='BYTE_COLOR')
					x.data.attributes.active_color.name = "td_vis"

				x.data.vertex_colors["td_vis"].active = True

				# Get UV islands
				if td.bake_vc_mode == "UV_ISLANDS_TO_VC" and td.uv_islands_to_vc_mode == "OVERLAP":
					# Overlapping islands like one island
					islands_list = bpy_extras.mesh_utils.mesh_linked_uv_islands(bpy.context.active_object.data)
				else:
					# Overlapping islands like separated islands
					islands_list = utils.Get_UV_Islands()

				# Get TD and UV Area for each polygon (TD, Area)
				face_td_area_list = utils.Calculate_TD_Area_To_List_CPP()

				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()

				# Calculate and assign color from TD to VC for each polygon
				if td.bake_vc_mode == "TD_FACES_TO_VC":
					for face_id in range(0, face_count):
						color = colorize(face_td_area_list[face_id * 2], bake_vc_min_td, bake_vc_max_td)

						for loop in bm.faces[face_id].loops:
							loop[bm.loops.layers.color.get("td_vis")] = color

				# Assign random color for each island
				elif td.bake_vc_mode == "UV_ISLANDS_TO_VC":
					for uv_island in islands_list:
						random_hue = random.randrange(0, 10, 1) / 10
						random_value = random.randrange(2, 10, 1) / 10
						random_saturation = random.randrange(7, 10, 1) / 10
						color = colorsys.hsv_to_rgb(random_hue, random_saturation, random_value)
						color4 = (color[0], color[1], color[2], 1)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.get("td_vis")] = color4

				# Calculate and assign color from UV area to VC for each island (UV areas sum of polygons of island)
				elif td.bake_vc_mode == "UV_SPACE_TO_VC":
					for uv_island in islands_list:
						island_area = 0
						for face_id in uv_island:
							island_area += face_td_area_list[face_id * 2 + 1]

						# Convert island area value to percentage of area
						island_area *= 100
						color = colorize(island_area, bake_vc_min_space, bake_vc_max_space)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.get("td_vis")] = color

				# Calculate and assign color from TD to VC for each island (average TD between polygons of island)
				elif td.bake_vc_mode == "TD_ISLANDS_TO_VC":
					for uv_island in islands_list:
						island_td = 0
						island_area = 0

						# Calculate Total Island Area
						for face_id in uv_island:
							island_area += face_td_area_list[face_id * 2 + 1]

						if island_area == 0:
							island_area = 0.000001

						# Calculate Average Island TD
						for face_id in uv_island:
							island_td += face_td_area_list[face_id * 2] * face_td_area_list[face_id * 2 + 1] / island_area

						color = colorize(island_td, bake_vc_min_td, bake_vc_max_td)

						for face_id in uv_island:
							for loop in bm.faces[face_id].loops:
								loop[bm.loops.layers.color.get("td_vis")] = color

				elif td.bake_vc_mode == 'DISTORTION':
					uv_area_total = 0
					geom_area_total = 0
					geom_area_list = []

					# Get Total UV and Geometry areas and Geometry area for each poly
					for face_id in range(0, face_count):
						# Geometry Area
						gm_area = bpy.context.active_object.data.polygons[face_id].area
						geom_area_total += gm_area
						geom_area_list.append(gm_area)
						# Total UV Area
						uv_area_total += face_td_area_list[face_id * 2 + 1]

					# Protection from zero division
					if uv_area_total < 0.0001:
						uv_area_total = 0.0001
					if geom_area_total < 0.0001:
						geom_area_total = 0.0001

					# Calculate Min/Max for range
					min_range = 1 - (bake_vc_distortion_range / 100)
					if min_range < 0:
						min_range = 0
					max_range = 1 + (bake_vc_distortion_range / 100)

					for face_id in range(0, face_count):
						uv_percent = face_td_area_list[face_id * 2 + 1] / uv_area_total
						geom_percent = geom_area_list[face_id] / geom_area_total

						color = colorize(uv_percent / geom_percent, min_range, max_range)

						for loop in bm.faces[face_id].loops:
							loop[bm.loops.layers.color.get("td_vis")] = color

				bpy.ops.object.mode_set(mode='OBJECT')

				if start_mode == "EDIT":
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.object.mode_set(mode='OBJECT')
					for face_id in start_selected_faces:
						bpy.context.active_object.data.polygons[face_id].select = True

		bpy.ops.object.select_all(action='DESELECT')

		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj

		for j in need_select_again_obj:
			j.select_set(True)

		# Activate VC shading in viewport and show gradient line
		bpy.context.space_data.shading.color_type = 'VERTEX'
		if td.bake_vc_mode == 'TD_FACES_TO_VC' or td.bake_vc_mode == 'TD_ISLANDS_TO_VC' \
				or td.bake_vc_mode == 'UV_SPACE_TO_VC' or td.bake_vc_mode == 'DISTORTION':
			props.Show_Gradient(self, context)

		utils.Print_Execution_Time("Bake TD to VC", start_time)
		return {'FINISHED'}


# Clear Baked TD or UV area form VC
class Clear_TD_VC(bpy.types.Operator):
	"""Clear TD Baked into Vertex Color"""
	bl_idname = "object.clear_td_vc"
	bl_label = "Clear Vertex Color from TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		start_mode = bpy.context.object.mode
		start_active_obj = bpy.context.active_object
		need_select_again_obj = bpy.context.selected_objects

		if start_mode == 'EDIT':
			start_selected_obj = bpy.context.objects_in_mode
		else:
			start_selected_obj = bpy.context.selected_objects

		for obj in start_selected_obj:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			if obj.type == 'MESH':
				bpy.context.view_layer.objects.active = obj
				bpy.context.view_layer.objects.active.select_set(True)

				# Delete vertex color for baked TD or UV area
				if len(obj.data.vertex_colors) > 0:
					for vc in obj.data.vertex_colors:
						if vc.name == "td_vis":
							vc.active = True
							bpy.ops.geometry.color_attribute_remove()

		bpy.ops.object.select_all(action='DESELECT')
		if start_mode == 'EDIT':
			for o in start_selected_obj:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.mode_set(mode='EDIT')

		bpy.context.view_layer.objects.active = start_active_obj
		for j in need_select_again_obj:
			j.select_set(True)

		utils.Print_Execution_Time("Clear Baked TD from VC", start_time)
		return {'FINISHED'}


classes = (
	Checker_Assign,
	Checker_Restore,
	Clear_Saved_Materials,
	Bake_TD_UV_to_VC,
	Clear_TD_VC,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
