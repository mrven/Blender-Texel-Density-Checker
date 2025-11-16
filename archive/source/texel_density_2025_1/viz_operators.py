import bpy
import bmesh
import math
import colorsys
import blf
import gpu
import random
import bpy_extras.mesh_utils
import numpy as np

from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty
from datetime import datetime

from . import utils
from . import props
from .constants import *
from .cpp_interface import TDCoreWrapper

# Draw Reference Gradient Line for Color Visualizer
def draw_callback_px(_, __):
	td = bpy.context.scene.td
	version = bpy.app.version

	# Get Parameters
	region = bpy.context.region
	screen_texel_x = 2 / region.width  # 2 because Screen Space -1.0 to 1.0
	screen_texel_y = 2 / region.height

	font_size = 12
	offset_x = int(bpy.context.preferences.addons[__package__].preferences.offset_x)
	offset_y = int(bpy.context.preferences.addons[__package__].preferences.offset_y)
	anchor_pos = bpy.context.preferences.addons[__package__].preferences.anchor_pos
	font_id = 0

	if version < (3, 6, 0):
		blf.size(font_id, font_size, 72)
	else:
		blf.size(font_id, font_size)

	blf.color(font_id, 1, 1, 1, 1)

	bake_min_value = 0
	bake_max_value = 0

	if td.bake_vc_mode in {"TD_FACES_TO_VC", "TD_ISLANDS_TO_VC"}:
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

	# Gradient Bounds with range 0.0 - 2.0
	gradient_line_width = 250
	gradient_line_height = 15

	gradient_x_min = screen_texel_x * offset_x
	gradient_x_max = screen_texel_x * (offset_x + gradient_line_width)
	gradient_y_min = screen_texel_y * offset_y
	gradient_y_max = screen_texel_y * (offset_y + gradient_line_height)

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

	if version < (3, 3, 0):
		shader = gpu.types.GPUShader(VERTEX_SHADER_TEXT_3_0, FRAGMENT_SHADER_TEXT_3_0)
		batch = batch_for_shader(shader, 'TRIS', {"position": vertices}, indices=indices)
	else:
		# Draw Gradient Line via Shader
		vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
		vert_out.smooth('VEC3', "pos")

		shader_info = gpu.types.GPUShaderCreateInfo()
		shader_info.push_constant('FLOAT', "pos_x_min")
		shader_info.push_constant('FLOAT', "pos_x_max")
		shader_info.vertex_in(0, 'VEC2', "position")
		shader_info.vertex_out(vert_out)
		shader_info.fragment_out(0, 'VEC4', "FragColor")

		shader_info.vertex_source(VERTEX_SHADER_TEXT_3_3)
		shader_info.fragment_source(FRAGMENT_SHADER_TEXT_3_3)

		shader = gpu.shader.create_from_info(shader_info)
		del vert_out
		del shader_info

		batch = batch_for_shader(shader, 'TRIS', {"position": vertices}, indices=indices)

	shader.bind()
	shader.uniform_float("pos_x_min", pos_x_min)
	shader.uniform_float("pos_x_max", pos_x_max)
	batch.draw(shader)


# Assign of Checker Material
class CheckerAssign(bpy.types.Operator):
	"""Assign of checker material"""
	bl_idname = "texel_density.material_assign"
	bl_label = "Assign Checker Material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td
		start_mode = context.object.mode
		start_active_obj = context.active_object
		need_select_again_obj = context.selected_objects
		start_selected_obj = context.objects_in_mode if start_mode == 'EDIT' else context.selected_objects

		# Get texture size from panel
		checker_resolution_x, checker_resolution_y = utils.get_texture_resolution()

		# Get or create checker texture
		td_checker_texture = next((tex for tex in bpy.data.images if tex.is_td_texture), None)
		if not td_checker_texture:
			td_checker_texture = bpy.data.images.new(TD_MATERIAL_NAME, width=checker_resolution_x, height=checker_resolution_y)
			td_checker_texture.generated_type = td.checker_type
			td_checker_texture.is_td_texture = True
		else:
			td_checker_texture.generated_width = checker_resolution_x
			td_checker_texture.generated_height = checker_resolution_y
			td_checker_texture.generated_type = td.checker_type

		# Get or create checker material
		td_checker_material = next((mat for mat in bpy.data.materials if mat.is_td_material), None)
		if not td_checker_material:
			td_checker_material = bpy.data.materials.new(TD_MATERIAL_NAME)
			td_checker_material.is_td_material = True
			td_checker_material.use_nodes = True

			nodes = td_checker_material.node_tree.nodes
			links = td_checker_material.node_tree.links
			nodes.clear()

			output_node = nodes.new('ShaderNodeOutputMaterial')
			output_node.location = (300, 200)

			bsdf = nodes.new('ShaderNodeBsdfPrincipled')
			bsdf.location = (0, 200)
			links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

			mix_node = nodes.new('ShaderNodeMixRGB')
			mix_node.location = (-200, 200)
			mix_node.blend_type = 'COLOR'
			mix_node.inputs['Fac'].default_value = 1.0
			links.new(mix_node.outputs['Color'], bsdf.inputs['Base Color'])

			tex_node = nodes.new('ShaderNodeTexImage')
			tex_node.location = (-500, 300)
			tex_node.image = td_checker_texture
			tex_node.interpolation = 'Closest'
			links.new(tex_node.outputs['Color'], mix_node.inputs['Color1'])

			vc_node = nodes.new('ShaderNodeAttribute')
			vc_node.location = (-500, 0)
			vc_node.attribute_name = TD_VC_NAME
			links.new(vc_node.outputs['Color'], mix_node.inputs['Color2'])

			uv_map = nodes.new('ShaderNodeUVMap')
			uv_map.location = (-1000, 220)

			mapping = nodes.new('ShaderNodeMapping')
			mapping.location = (-800, 300)
			mapping.inputs['Scale'].default_value[0] = float(td.checker_uv_scale)
			mapping.inputs['Scale'].default_value[1] = float(td.checker_uv_scale)

			links.new(uv_map.outputs['UV'], mapping.inputs['Vector'])
			links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])

		bpy.ops.object.mode_set(mode='OBJECT')

		bm = bmesh.new()

		if td.checker_method == 'STORE':
			for obj in start_selected_obj:
				if obj.type != 'MESH' or obj.td_settings:
					continue
				bm.clear()
				bm.from_mesh(obj.data)
				bm.faces.ensure_lookup_table()
				for face in bm.faces:
					obj.td_settings.add().mat_index = face.material_index

		bm.free()

		# Remove all materials if REPLACE method
		if td.checker_method == 'REPLACE':
			for obj in start_selected_obj:
				if obj.type == 'MESH':
					obj.data.materials.clear()
					obj.data.materials.append(td_checker_material)

		# For STORE method, only assign if not already assigned
		if td.checker_method == 'STORE':
			for obj in start_selected_obj:
				if obj.type != 'MESH':
					continue

				if any(mat and mat.is_td_material for mat in obj.data.materials):
					continue

				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.view_layer.objects.active = obj
				obj.select_set(True)

				obj.data.materials.append(td_checker_material)
				mat_index = len(obj.data.materials) - 1
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')
				obj.active_material_index = mat_index
				bpy.ops.object.material_slot_assign()
				bpy.ops.object.mode_set(mode='OBJECT')

		# Restore original selection and mode
		bpy.ops.object.select_all(action='DESELECT')
		for obj in need_select_again_obj:
			obj.select_set(True)

		context.view_layer.objects.active = start_active_obj
		if start_mode == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')

		utils.print_execution_time("Assign of Checker Material", start_time)
		return {'FINISHED'}


# Restore Real Materials
class CheckerRestore(bpy.types.Operator):
	"""Restores original materials saved before applying the checker material"""
	bl_idname = "texel_density.material_restore"
	bl_label = "Restore Materials"
	bl_options = {'REGISTER'}

	def execute(self, context):
		start_time = datetime.now()
		start_mode = context.object.mode
		start_active_obj = context.active_object
		need_select_again_obj = context.selected_objects
		start_selected_obj = context.objects_in_mode if start_mode == 'EDIT' else context.selected_objects

		bpy.ops.object.mode_set(mode='OBJECT')

		bm = bmesh.new()

		for obj in start_selected_obj:
			if obj.type != 'MESH':
				continue

			context.view_layer.objects.active = obj
			obj.select_set(True)

			if len(obj.td_settings) > 0:
				# Get material indices
				mat_indices = np.fromiter((s.mat_index for s in obj.td_settings), dtype=np.int32)

				# Restore material indices
				bm.clear()
				bm.from_mesh(obj.data)
				bm.faces.ensure_lookup_table()

				for face, mat_index in zip(bm.faces, mat_indices):
					face.material_index = int(mat_index)

				bm.to_mesh(obj.data)

				# Clear stored settings
				obj.td_settings.clear()

			# Remove TD material(s)
			mats = obj.data.materials
			remove_indices = [i for i, m in enumerate(mats) if m and m.is_td_material]

			for i in reversed(remove_indices):
				mats.pop(index=i)

		bm.free()

		# Restore original selection and mode
		bpy.ops.object.select_all(action='DESELECT')
		for obj in need_select_again_obj:
			obj.select_set(True)

		context.view_layer.objects.active = start_active_obj
		if start_mode == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')

		utils.print_execution_time("Restore Materials", start_time)
		return {'FINISHED'}


# Clear Saved Real Materials assignment from Objects
class ClearSavedMaterials(bpy.types.Operator):
	"""Clear original materials assignment saved before applying the checker material"""
	bl_idname = "texel_density.material_clear"
	bl_label = "Clear Stored Materials"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		start_mode = context.object.mode
		start_selected_obj = context.objects_in_mode if start_mode == 'EDIT' else context.selected_objects

		bpy.ops.object.mode_set(mode='OBJECT')

		for obj in start_selected_obj:
			if obj.type == 'MESH':
				obj.td_settings.clear()

		if start_mode == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')

		utils.print_execution_time("Clear Saved Materials", start_time)
		return {'FINISHED'}


# Bake TD to VC
class BakeTDToVC(bpy.types.Operator):
	"""Visualize TD/Islands/UV with vertex color"""
	bl_idname = "texel_density.vc_bake"
	bl_label = "Bake TD to Vertex Color"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		td = context.scene.td
		version = bpy.app.version
		start_active_obj = context.active_object
		start_mode = context.object.mode
		need_select_again_obj = context.selected_objects
		start_selected_obj = context.objects_in_mode if start_mode == 'EDIT' else context.selected_objects

		# Range for baking TD
		bake_vc_min_td = float(td.bake_vc_min_td)
		bake_vc_max_td = float(td.bake_vc_max_td)
		# Range for baking UV Space
		bake_vc_min_space = float(td.bake_vc_min_space)
		bake_vc_max_space = float(td.bake_vc_max_space)
		# Range for baking UV Distortion
		bake_vc_distortion_range = float(td.bake_vc_distortion_range)

		bpy.ops.object.mode_set(mode='OBJECT')

		# Calculate TD and UV Area for all objects
		td_area_map = {}

		tdcore_lib = TDCoreWrapper() if utils.get_preferences().calculation_backend == 'CPP' else None

		for obj in start_selected_obj:
			if obj.type != 'MESH' or len(obj.data.uv_layers) == 0 or len(obj.data.polygons) == 0:
				continue

			bpy.ops.object.select_all(action='DESELECT')
			context.view_layer.objects.active = obj
			obj.select_set(True)

			td_area_map[obj.name] = utils.calculate_td_area_to_list(tdcore_lib)

		# Automatic Min/Max TD
		if td.bake_vc_auto_min_max and (td.bake_vc_mode in {'TD_FACES_TO_VC', 'TD_ISLANDS_TO_VC'}):
			min_td = float('inf')
			max_td = float('-inf')

			for td_list in td_area_map.values():
				for td_val, _ in td_list:
					min_td = min(min_td, td_val)
					max_td = max(max_td, td_val)

			if min_td != float('inf') and max_td != float('-inf'):
				td.bake_vc_min_td = f"{min_td:.3f}"
				td.bake_vc_max_td = f"{max_td:.3f}"
				bake_vc_min_td = min_td
				bake_vc_max_td = max_td

		bm = bmesh.new()

		for obj in start_selected_obj:
			if obj.type != 'MESH' or len(obj.data.uv_layers) == 0 or len(obj.data.polygons) == 0:
				continue

			bpy.ops.object.select_all(action='DESELECT')
			context.view_layer.objects.active = obj
			obj.select_set(True)

			mesh_data = obj.data

			start_selected_faces = None

			# Save selected faces
			if start_mode == "EDIT":
				start_selected_faces = np.array([
						p.index for p in mesh_data.polygons if p.select
					], dtype=np.int32)

			# Add vertex color group for visualization over material
			if TD_VC_NAME not in mesh_data.vertex_colors:
				if version < (3, 3, 0):
					bpy.ops.mesh.vertex_color_add()
					mesh_data.vertex_colors.active.name = TD_VC_NAME
				else:
					bpy.ops.geometry.color_attribute_add(domain='CORNER', data_type='BYTE_COLOR')
					mesh_data.attributes.active_color.name = TD_VC_NAME

			mesh_data.vertex_colors[TD_VC_NAME].active = True

			# Get UV islands
			if td.bake_vc_mode == "UV_ISLANDS_TO_VC" and td.uv_islands_to_vc_mode == "OVERLAP":
				# Overlapping islands like one island
				islands_list = bpy_extras.mesh_utils.mesh_linked_uv_islands(mesh_data)
			elif td.bake_vc_mode in {'UV_ISLANDS_TO_VC', 'UV_SPACE_TO_VC', 'TD_ISLANDS_TO_VC'}:
				# Overlapping islands like separated islands
				islands_list = utils.get_uv_islands()
			else:
				islands_list = []

			# Get TD and UV Area for each polygon (TD, Area)
			face_td_area_list = td_area_map.get(obj.name)

			if not face_td_area_list:
				continue

			bm.clear()
			bm.from_mesh(obj.data)
			bm.faces.ensure_lookup_table()

			color_layer = bm.loops.layers.color.get(TD_VC_NAME)

			# Calculate and assign color from TD to VC for each polygon
			if td.bake_vc_mode == "TD_FACES_TO_VC":
				td_values = np.array(face_td_area_list, dtype=np.float32)[:, 0]
				colors = utils.value_to_color(td_values.tolist(), bake_vc_min_td, bake_vc_max_td, tdcore_lib)

				for face, color in zip(bm.faces, colors):
					for loop in face.loops:
						loop[color_layer] = color

			# Assign random color for each island
			elif td.bake_vc_mode == "UV_ISLANDS_TO_VC":
				for uv_island in islands_list:
					hue = random.randint(0, 9) / 10
					saturation = random.randint(7, 9) / 10
					value = random.randint(2, 9) / 10
					r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
					color = (r, g, b, 1)

					for face_id in uv_island:
						for loop in bm.faces[face_id].loops:
							loop[color_layer] = color

			# Calculate and assign color from UV area to VC for each island (UV areas sum of polygons of island)
			elif td.bake_vc_mode == "UV_SPACE_TO_VC":
				island_areas = []
				for uv_island in islands_list:
					island_area = 0
					for face_id in uv_island:
						island_area += face_td_area_list[face_id][1]

					# Convert island area value to percentage of area
					island_areas.append(island_area * 100)

				colors = utils.value_to_color(island_areas, bake_vc_min_space, bake_vc_max_space, tdcore_lib)

				for color, uv_island in zip(colors, islands_list):
					for face_id in uv_island:
						for loop in bm.faces[face_id].loops:
							loop[color_layer] = color

			# Calculate and assign color from TD to VC for each island (average TD between polygons of island)
			elif td.bake_vc_mode == "TD_ISLANDS_TO_VC":
				td_area_array = np.asarray(face_td_area_list, dtype=np.float32)
				td_vals = td_area_array[:, 0]
				uv_areas = td_area_array[:, 1]

				islands_td = np.array([
					np.dot(td_vals[island], uv_areas[island]) / max(uv_areas[island].sum(), 0.0001)
					for island in islands_list
				], dtype=np.float32)

				colors = utils.value_to_color(islands_td.tolist(), bake_vc_min_td, bake_vc_max_td, tdcore_lib)

				for color, uv_island in zip(colors, islands_list):
					for face_id in uv_island:
						for loop in bm.faces[face_id].loops:
							loop[color_layer] = color

			elif td.bake_vc_mode == 'DISTORTION':
				geom_areas = [p.area for p in mesh_data.polygons]
				uv_areas = [uv_area for _, uv_area in face_td_area_list]

				geom_area_total = sum(geom_areas)
				uv_area_total = sum(uv_areas)

				geom_area_total = max(geom_area_total, 0.0001)
				uv_area_total = max(uv_area_total, 0.0001)

				min_range = max(0, 1 - (bake_vc_distortion_range / 100))
				max_range = 1 + (bake_vc_distortion_range / 100)

				distortions = []

				for face, geom_area, uv_area in zip(bm.faces, geom_areas, uv_areas):
					uv_percent = uv_area / uv_area_total
					geom_percent = geom_area / geom_area_total
					distortion_ratio = uv_percent / geom_percent
					distortions.append(distortion_ratio)

				colors = utils.value_to_color(distortions, min_range, max_range, tdcore_lib)

				for color, face in zip(colors, bm.faces):
					for loop in face.loops:
						loop[color_layer] = color

			bm.to_mesh(obj.data)

			if start_mode == "EDIT" and start_selected_faces is not None:
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				for face_id in start_selected_faces:
					mesh_data.polygons[face_id].select = True

		bm.free()

		# Restore original selection and mode
		bpy.ops.object.select_all(action='DESELECT')
		for obj in need_select_again_obj:
			obj.select_set(True)

		context.view_layer.objects.active = start_active_obj
		if start_mode == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')

		# Activate VC shading in viewport and show gradient line
		context.space_data.shading.color_type = 'VERTEX'
		if td.bake_vc_mode in {'TD_FACES_TO_VC', 'TD_ISLANDS_TO_VC', 'UV_SPACE_TO_VC', 'DISTORTION'}:
			props.show_gradient(self, context)

		utils.print_execution_time("Bake TD to VC", start_time)
		return {'FINISHED'}


# Clear Baked TD or UV area form VC
class ClearTDFromVC(bpy.types.Operator):
	"""Clear baked values from vertex colors"""
	bl_idname = "texel_density.vc_clear"
	bl_label = "Clear TD Vertex Colors"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		version = bpy.app.version
		start_mode = context.object.mode
		start_active_obj = context.active_object
		need_select_again_obj = context.selected_objects
		start_selected_obj = context.objects_in_mode if start_mode == 'EDIT' else context.selected_objects

		bpy.ops.object.mode_set(mode='OBJECT')

		for obj in start_selected_obj:
			if obj.type == 'MESH':
				bpy.ops.object.select_all(action='DESELECT')
				context.view_layer.objects.active = obj
				obj.select_set(True)

				# Delete vertex color for baked TD or UV area
				if TD_VC_NAME in obj.data.vertex_colors:
					obj.data.vertex_colors[TD_VC_NAME].active = True
					if version < (3, 3, 0):
						bpy.ops.mesh.vertex_color_remove()
					else:
						bpy.ops.geometry.color_attribute_remove()

		# Restore original selection and mode
		bpy.ops.object.select_all(action='DESELECT')
		for obj in need_select_again_obj:
			obj.select_set(True)

		context.view_layer.objects.active = start_active_obj
		if start_mode == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')

		utils.print_execution_time("Clear Baked TD from VC", start_time)
		return {'FINISHED'}


classes = (
	CheckerAssign,
	CheckerRestore,
	ClearSavedMaterials,
	BakeTDToVC,
	ClearTDFromVC,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
