import bpy
import bmesh
import colorsys
from datetime import datetime
import os
import ctypes
import ctypes.util
import numpy as np
import sys
import math
from collections import defaultdict

from .cpp_interface import TDCoreWrapper

def sync_uv_selection():
	mesh = bpy.context.active_object.data
	bm = bmesh.from_edit_mesh(mesh)
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active
	td = bpy.context.scene.td

	uv_selected_faces = []

	for face in bm.faces:
		if face.select:
			if all(loop[uv_layer].select for loop in face.loops):
				uv_selected_faces.append(face.index)

	for face in bm.faces:
		for loop in face.loops:
			loop[uv_layer].select = False

	for face_id in uv_selected_faces:
		for loop in bm.faces[face_id].loops:
			loop[uv_layer].select = True

	for face in bm.faces:
		face.select_set(not td.selected_faces)

	for face_id in uv_selected_faces:
		bm.faces[face_id].select_set(True)

	bmesh.update_edit_mesh(mesh)


def calculate_geometry_areas(obj):
	mesh = obj.data
	world_matrix = obj.matrix_world

	areas = []

	for poly in mesh.polygons:
		verts_world = [world_matrix @ obj.data.vertices[i].co for i in poly.vertices]

		if len(verts_world) == 3:
			v1 = verts_world[1] - verts_world[0]
			v2 = verts_world[2] - verts_world[0]
			area = 0.5 * (v1.cross(v2)).length

		else:
			area = 0
			for i in range(1, len(verts_world) - 1):
				v1 = verts_world[i] - verts_world[0]
				v2 = verts_world[i + 1] - verts_world[0]
				area += 0.5 * (v1.cross(v2)).length

		areas.append(area)

	return areas


def calculate_td_area_to_list(tdcore):
	backend = get_preferences().calculation_backend
	td = bpy.context.scene.td

	start_obj = bpy.context.active_object
	start_mode = start_obj.mode

	texture_size_x, texture_size_y = get_texture_resolution()
	aspect_ratio = texture_size_x / texture_size_y
	if aspect_ratio < 1:
		aspect_ratio = 1 / aspect_ratio
	largest_side = max(texture_size_x, texture_size_y)
	scale = (largest_side / math.sqrt(aspect_ratio)) / (100 * bpy.context.scene.unit_settings.scale_length)

	bpy.ops.object.mode_set(mode='OBJECT')

	obj = bpy.context.active_object
	mesh_data = obj.data
	mesh_data.calc_loop_triangles()

	face_areas = calculate_geometry_areas(obj)
	uv_layer = mesh_data.uv_layers.active.data

	result = []

	if backend == 'CPP' and tdcore:
		# Get UV-coordinates
		uvs = np.empty(len(uv_layer) * 2, dtype=np.float32)
		uv_layer.foreach_get("uv", uvs)
		uvs = uvs.reshape(-1, 2).flatten()

		areas = np.array(face_areas, dtype=np.float32)

		# Get Vertex Count
		vertex_counts = np.empty(len(mesh_data.polygons), dtype=np.int32)
		mesh_data.polygons.foreach_get("loop_total", vertex_counts)

		# Results Buffer (Poly Count * 2 float: TD and uv_area)
		result_cpp = np.zeros(len(mesh_data.polygons) * 2, dtype=np.float32)

		# Call function from Library
		tdcore.lib.CalculateTDAreaArray(
			uvs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
			uvs.size,
			areas.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
			vertex_counts.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
			areas.size,
			scale,
			int(td.units),
			result_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
		)

		result = list(map(tuple, result_cpp.reshape(-1, 2)))
	else:
		uv_area_by_face = defaultdict(float)

		for tri in mesh_data.loop_triangles:
			face_index = tri.polygon_index
			loops = tri.loops

			uv0 = uv_layer[loops[0]].uv
			uv1 = uv_layer[loops[1]].uv
			uv2 = uv_layer[loops[2]].uv

			u = uv1 - uv0
			v = uv2 - uv0
			cross = u.x * v.y - u.y * v.x
			uv_area = 0.5 * abs(cross)

			uv_area_by_face[face_index] += uv_area

		for face_index, uv_area in uv_area_by_face.items():
			geo_area = face_areas[face_index]

			if geo_area > 0 and uv_area > 0:
				texel_density = scale * math.sqrt(uv_area) / math.sqrt(geo_area)
			else:
				texel_density = 0.0001

			if td.units == '1':
				texel_density *= 100.0
			elif td.units == '2':
				texel_density *= 2.54
			elif td.units == '3':
				texel_density *= 30.48

			result.append([texel_density, uv_area])

	bpy.context.view_layer.objects.active = start_obj
	bpy.ops.object.mode_set(mode=start_mode)

	return result


def get_texture_resolution():
	td = bpy.context.scene.td

	if td.texture_size != 'CUSTOM':
		try:
			res = int(td.texture_size)
			return res, res
		except Exception as e:
			print(f"[WARNING] Failed convert Texture Size to int {e}")
			return 1024, 1024

	try:
		texture_resolution_x = int(td.custom_width)
	except Exception as e:
		print(f"[WARNING] Failed convert Texture Size X to int {e}")
		td['custom_width'] = '1024'
		texture_resolution_x = 1024

	try:
		texture_resolution_y = int(td.custom_height)
	except Exception as e:
		print(f"[WARNING] Failed convert Texture Size Y to int {e}")
		td['custom_height'] = '1024'
		texture_resolution_y = 1024

	if texture_resolution_x < 1 or texture_resolution_y < 1:
		td['custom_width'] = '1024'
		td['custom_height'] = '1024'
		return 1024, 1024

	return texture_resolution_x, texture_resolution_y


# Value by range to Color gradient by hue
def value_to_color(values, range_min, range_max, tdcore):
	td = bpy.context.scene.td
	backend = get_preferences().calculation_backend

	result = []

	if backend == 'CPP' and tdcore:
		# Results Buffer (values count * RGBA (4 floats))
		result_cpp = np.zeros(len(values) * 4, dtype=np.float32)
		values_np = np.array(values, dtype=np.float32)

		# Call function from Library
		tdcore.lib.ValueToColor(
			values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
			len(values),
			ctypes.c_float(range_min),
			ctypes.c_float(range_max),
			result_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
		)

		result = [tuple(result_cpp[i:i + 4]) for i in range(0, len(result_cpp), 4)]
	else:
		for value in values:
			# Remap value to range 0.0 - 1.0
			remapped_value = 0.5

			if abs(range_max - range_min) > 0.001:
				remapped_value = saturate((value - range_min) / (range_max - range_min))

			# Calculate hue and get color
			hue = (1 - remapped_value) * 0.67
			r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)

			result.append((r, g, b, 1))

	return result


# Get list of islands
def get_uv_islands():
	obj = bpy.context.active_object
	start_mode = obj.mode
	bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(obj.data)
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active
	face_count = len(bm.faces)

	start_selected_3d_faces = {f.index for f in bm.faces if f.select}
	start_hidden_faces = {f.index for f in bm.faces if f.hide}
	start_selected_uv_faces = {f.index for f in bm.faces if all(loop[uv_layer].select for loop in f.loops)}

	scene = bpy.context.scene
	start_uv_sync = scene.tool_settings.use_uv_select_sync
	scene.tool_settings.use_uv_select_sync = False

	bpy.ops.mesh.reveal()
	bpy.ops.mesh.select_all(action='SELECT')

	remaining_faces = set(range(face_count))
	uv_islands = []

	while remaining_faces:
		seed_face_idx = next(iter(remaining_faces))

		bpy.ops.uv.select_all(action='DESELECT')
		for loop in bm.faces[seed_face_idx].loops:
			loop[uv_layer].select = True

		bpy.ops.uv.select_linked()

		current_island = []
		for face_idx in list(remaining_faces):
			face = bm.faces[face_idx]
			if face.select and all(loop[uv_layer].select for loop in face.loops):
				current_island.append(face_idx)

		if not current_island:
			print("Warning: Could not select UV island properly.")
			break

		uv_islands.append(current_island)

		remaining_faces.difference_update(current_island)

	bpy.ops.mesh.select_all(action='DESELECT')
	scene.tool_settings.use_uv_select_sync = start_uv_sync
	bpy.ops.uv.select_all(action='DESELECT')

	for face_idx in start_selected_3d_faces:
		bm.faces[face_idx].select = True

	for face_idx in start_selected_uv_faces:
		for loop in bm.faces[face_idx].loops:
			loop[uv_layer].select = True

	for face_idx in start_hidden_faces:
		bm.faces[face_idx].hide_set(True)

	bmesh.update_edit_mesh(obj.data)
	bpy.ops.object.mode_set(mode=start_mode)

	return uv_islands


def saturate(val):
	return max(min(val, 1), 0)


# Execution Time
def print_execution_time(function_name, start_time):
	td = bpy.context.scene.td

	if td.debug:
		finish_time = datetime.now()
		execution_time = finish_time - start_time
		seconds = (execution_time.total_seconds())
		milliseconds = round(seconds * 1000)
		print(function_name + " finished in " + str(seconds) + "s (" + str(milliseconds) + "ms)")


def get_preferences():
	preferences = bpy.context.preferences
	addon_prefs = preferences.addons[__package__].preferences

	return addon_prefs