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


def calculate_td_area_to_list():
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

	tdcore = None

	if backend == 'CPP':
		# Get Library
		tdcore = get_td_core_dll()

		if tdcore:
			tdcore.CalculateTDAreaArray.argtypes = [
				ctypes.POINTER(ctypes.c_float),  # UVs
				ctypes.c_int,  # UVs Count
				ctypes.POINTER(ctypes.c_float),  # Areas
				ctypes.POINTER(ctypes.c_int),  # Vertex Count by Polygon
				ctypes.c_int,  # Poly Count
				ctypes.c_float,  # Scale
				ctypes.c_int,  # Units
				ctypes.POINTER(ctypes.c_float)  # Results
			]

			tdcore.CalculateTDAreaArray.restype = None

	bpy.ops.object.mode_set(mode='OBJECT')

	bpy.ops.object.duplicate()
	bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

	obj = bpy.context.active_object
	mesh_data = obj.data
	mesh_data.calc_loop_triangles()

	face_areas = [p.area for p in mesh_data.polygons]
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
		tdcore.CalculateTDAreaArray(
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

		free_td_core_dll(tdcore)
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

	mesh_name = mesh_data.name
	bpy.ops.object.delete()
	try:
		bpy.data.meshes.remove(bpy.data.meshes[mesh_name])
	except Exception:
		pass

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
def value_to_color(value, range_min, range_max):
	# Remap value to range 0.0 - 1.0
	if range_min == range_max or abs(range_max - range_min) < 0.001:
		remapped_value = 0.5
	else:
		remapped_value = (value - range_min) / (range_max - range_min)
		remapped_value = saturate(remapped_value)

	# Calculate hue and get color
	hue = (1 - remapped_value) * 0.67
	color = colorsys.hsv_to_rgb(hue, 1, 1)
	color4 = (color[0], color[1], color[2], 1)
	return color4


# Get list of islands (slow)
def get_uv_islands():
	start_selected_3d_faces = []
	start_selected_uv_faces = []
	start_hidden_faces = []
	start_mode = bpy.context.object.mode
	start_uv_sync_mode = bpy.context.scene.tool_settings.use_uv_select_sync

	bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active
	face_count = len(bm.faces)

	# Save start selected and hidden faces
	for face in bm.faces:
		if face.select:
			start_selected_3d_faces.append(face.index)
		if face.hide:
			start_hidden_faces.append(face.index)

		face_is_uv_selected = True
		for loop in face.loops:
			if not loop[uv_layer].select:
				face_is_uv_selected = False

		if face_is_uv_selected:
			start_selected_uv_faces.append(face.index)

	bpy.context.scene.tool_settings.use_uv_select_sync = False
	bpy.ops.mesh.reveal()
	bpy.ops.mesh.select_all(action='SELECT')

	face_dict = [f for f in range(0, face_count)]
	uv_islands = []

	face_dict_len_start = len(face_dict)
	face_dict_len_finish = 0

	while len(face_dict) > 0:
		if face_dict_len_finish == face_dict_len_start:
			print("Can not Select Island")
			uv_islands = []
			break

		face_dict_len_start = len(face_dict)

		uv_island = []
		bpy.ops.uv.select_all(action='DESELECT')

		for loop in bm.faces[face_dict[0]].loops:
			loop[uv_layer].select = True

		bpy.ops.uv.select_linked()

		for face_id in range(face_count):
			face_is_selected = True
			for loop in bm.faces[face_id].loops:
				if not loop[uv_layer].select:
					face_is_selected = False

			if face_is_selected and bm.faces[face_id].select:
				uv_island.append(face_id)

		for face_id in uv_island:
			face_dict.remove(face_id)

		face_dict_len_finish = len(face_dict)

		bpy.ops.uv.select_all(action='DESELECT')

		uv_islands.append(uv_island)

	# Restore Saved Parameters
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.context.scene.tool_settings.use_uv_select_sync = start_uv_sync_mode
	bpy.ops.uv.select_all(action='DESELECT')

	for face_id in start_selected_3d_faces:
		bm.faces[face_id].select = True

	for face_id in start_selected_uv_faces:
		for loop in bm.faces[face_id].loops:
			loop[uv_layer].select = True

	for face_id in start_hidden_faces:
		bm.faces[face_id].hide_set(True)

	bmesh.update_edit_mesh(bpy.context.active_object.data)

	bpy.ops.object.mode_set(mode=start_mode)

	return uv_islands


# Example for use get_selected_islands()

# data = bpy.context.active_object.data
# bm = bmesh.from_edit_mesh(data)
# uv_layers = bm.loops.layers.uv.verify()
# islands = get_selected_islands(bm, uv_layers)

# Get list of islands (fast)
def get_selected_islands(bm, uv_layers):
	islands = []
	island = []

	sync = bpy.context.scene.tool_settings.use_uv_select_sync

	faces = bm.faces
	# Reset tags for unselected (if tag is False - skip)
	if sync is False:
		for face in faces:
			face.tag = all(l[uv_layers].select for l in face.loops)
	else:
		for face in faces:
			face.tag = face.select

	for face in faces:
		# Skip unselected and appended faces
		if face.tag is False:
			continue

		# Tag first element in island (for don't add again)
		face.tag = False

		# Container collector of island elements
		parts_of_island = [face]

		# Conteiner for get elements from loop from parts_of_island
		temp = []

		# Blank list == all faces of the island taken
		while parts_of_island:
			for f in parts_of_island:
				# Running through all the neighboring faces
				for l in f.loops:
					link_face = l.link_loop_radial_next.face
					# Skip appended
					if link_face.tag is False:
						continue

					for ll in link_face.loops:
						if ll.face.tag is False:
							continue
						# If the coordinates of the vertices of adjacent
						# faces on the uv match, then this is part of the
						# island, and we append face to the list
						co = l[uv_layers].uv
						if ll[uv_layers].uv == co:
							temp.append(ll.face)
							ll.face.tag = False

			island.extend(parts_of_island)
			parts_of_island = temp
			temp = []
		islands.append(island)
		island = []
	return islands


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


def get_td_core_dll():
	if sys.platform.startswith("win"):
		lib_name = "tdcore.dll"
	elif sys.platform.startswith("linux"):
		lib_name = "libtdcore.so"
	elif sys.platform.startswith("darwin"):  # macOS
		lib_name = "libtdcore.dylib"
	else:
		return None

	addon_path = os.path.dirname(os.path.abspath(__file__))
	tdcore_path = os.path.join(addon_path, lib_name)

	if not os.path.isfile(tdcore_path):
		print(f"Library not found: {tdcore_path}")
		return None

	try:
		if sys.platform.startswith("win"):
			return ctypes.WinDLL(tdcore_path)  # Windows
		else:
			return ctypes.CDLL(tdcore_path)  # Linux/macOS
	except OSError as e:
		print(f"Failed to load library {tdcore_path}: {e}")
		return None


def free_td_core_dll(dll_handle):
	if not dll_handle or not hasattr(dll_handle, '_handle'):
		return

	try:
		handle = ctypes.c_void_p(dll_handle._handle)

		if sys.platform.startswith("win"):
			# Windows
			kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
			kernel32.FreeLibrary.argtypes = [ctypes.c_void_p]
			if not kernel32.FreeLibrary(handle):
				raise ctypes.WinError(ctypes.get_last_error())
		else:
			# Linux/Mac
			libc = ctypes.CDLL(None)
			libc.dlclose.argtypes = [ctypes.c_void_p]
			if libc.dlclose(handle) != 0:
				raise RuntimeError("Failed to dlclose library")
	except Exception as e:
		print(f"Warning: Library unload error: {str(e)}")
	finally:
		del dll_handle