import bpy
import bmesh
import colorsys
from datetime import datetime
import os
import ctypes
import ctypes.util
import numpy as np
import sys


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


def calculate_geometry_areas_cpp(obj):
	start_mode = bpy.context.object.mode

	# Get Library
	tdcore = get_td_core_dll()

	tdcore.CalculateGeometryAreas.argtypes = [
		ctypes.POINTER(ctypes.c_float),  # VertexCoordinates
		ctypes.POINTER(ctypes.c_float),  # MatrixWorld
		ctypes.c_int, # VertCount
		ctypes.c_int,  # PolyCount
		ctypes.POINTER(ctypes.c_int),  # Vertex Count by Polygon
		ctypes.POINTER(ctypes.c_float)  # Results
	]

	tdcore.CalculateGeometryAreas.restype = None

	bpy.ops.object.mode_set(mode='OBJECT')

	mesh_data = obj.data
	matrix_world = obj.matrix_world.transposed()
	poly_count = len(mesh_data.polygons)
	vertex_count = len(mesh_data.loops)

	# Get all vertex coordinates in from loops in LOCAL space as a flat array
	loop_vertex_indices = np.empty(len(mesh_data.loops), dtype=np.int32)
	mesh_data.loops.foreach_get("vertex_index", loop_vertex_indices)
	all_vertex_coords = np.empty(len(mesh_data.vertices) * 3, dtype=np.float32)
	mesh_data.vertices.foreach_get("co", all_vertex_coords)
	all_vertex_coords = all_vertex_coords.reshape(-1, 3)
	ordered_coords = all_vertex_coords[loop_vertex_indices]
	vert_co_ordered = ordered_coords.flatten().astype(np.float32)

	# Get world matrix and flatten it
	matrix_world = np.array(matrix_world, dtype=np.float32).flatten()

	# Get Vertex Count for each poly
	vertex_count_per_poly = np.empty(poly_count, dtype=np.int32)
	mesh_data.polygons.foreach_get("loop_total", vertex_count_per_poly)

	# Results Buffer (Geometry Area per Polygon)
	result = np.zeros(poly_count, dtype=np.float32)

	# Call function from Library
	tdcore.CalculateGeometryAreas(
		vert_co_ordered.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		matrix_world.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		vertex_count,
		poly_count,
		vertex_count_per_poly.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
		result.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
	)

	bpy.ops.object.mode_set(mode=start_mode)

	free_td_core_dll(tdcore)

	return result


# Calculate UV Area and Texel Density for each polygon with C++
def calculate_td_area_to_list_cpp(obj):
	td = bpy.context.scene.td

	# Save current mode
	start_mode = bpy.context.object.mode

	# Get Library
	tdcore = get_td_core_dll()

	tdcore.CalculateTDAreaArray.argtypes = [
		ctypes.POINTER(ctypes.c_float),  	# UVs
		ctypes.c_int,  						# UVs Count
		ctypes.POINTER(ctypes.c_float),  	# Areas
		ctypes.POINTER(ctypes.c_int),  		# Vertex Count by Polygon
		ctypes.c_int,  						# Poly Count
		ctypes.c_int,  						# Texture X Size
		ctypes.c_int,  						# Texture Y Size
		ctypes.c_float,  					# Scale Length
		ctypes.c_int,  						# Units
		ctypes.POINTER(ctypes.c_float)  	# Results
	]

	tdcore.CalculateTDAreaArray.restype = None

	# Get texture size from panel
	if td.texture_size != 'CUSTOM':
		texture_size_x = texture_size_y = int(td.texture_size)
	else:
		try:
			texture_size_x = int(td.custom_width)
		except Exception as e:
			print(f"[WARNING] Failed convert Texture Size X to int {e}")
			texture_size_x = 1024
		try:
			texture_size_y = int(td.custom_height)
		except Exception as e:
			print(f"[WARNING] Failed convert Texture Size X to int {e}")
			texture_size_y = 1024

	if texture_size_x < 1 or texture_size_y < 1:
		texture_size_x = 1024
		texture_size_y = 1024

	bpy.ops.object.mode_set(mode='OBJECT')

	mesh_data = obj.data

	# Get UV-coordinates
	uv_layer = mesh_data.uv_layers.active.data
	uvs = np.empty(len(uv_layer) * 2, dtype=np.float32)
	uv_layer.foreach_get("uv", uvs)
	uvs = uvs.reshape(-1, 2).flatten()

	# Get Geometry Area
	areas = calculate_geometry_areas_cpp(obj)

	# Get Vertex Count
	vertex_counts = np.empty(len(mesh_data.polygons), dtype=np.int32)
	mesh_data.polygons.foreach_get("loop_total", vertex_counts)

	# Results Buffer (Poly Count * 2 float: TD and uv_area)
	result = np.zeros(len(mesh_data.polygons) * 2, dtype=np.float32)

	# Call function from Library
	tdcore.CalculateTDAreaArray(
		uvs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		uvs.size,
		areas.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		vertex_counts.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
		areas.size,
		texture_size_x,
		texture_size_y,
		bpy.context.scene.unit_settings.scale_length,
		int(td.units),
		result.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
	)

	bpy.ops.object.mode_set(mode=start_mode)

	free_td_core_dll(tdcore)

	return result


def get_average_uv_center(obj, selected_polygons):
	mesh = obj.data
	uv_layer = mesh.uv_layers.active.data

	total_uv = np.array([0.0, 0.0], dtype=np.float64)
	count = 0

	for i, poly in enumerate(mesh.polygons):
		if selected_polygons[i] == 0:
			continue

		for loop_index in poly.loop_indices:
			uv = uv_layer[loop_index].uv
			total_uv += uv
			count += 1

	if count == 0:
		return 0.5, 0.5

	return total_uv / count


# Set TD
def set_texel_density_cpp(obj, selected_polygons, scale_origin_co, target_td, texture_size_x, texture_size_y, scale_mode):
	td = bpy.context.scene.td

	# Save current mode
	start_mode = bpy.context.object.mode

	# Get Library
	tdcore = get_td_core_dll()

	tdcore.SetTD.argtypes = [
		ctypes.POINTER(ctypes.c_float),	# UVs
		ctypes.c_int,					# UVs Count
		ctypes.POINTER(ctypes.c_float),	# Areas
		ctypes.POINTER(ctypes.c_int),	# Vertex Count (per poly)
		ctypes.c_int,					# Poly Count
		ctypes.c_int,					# Texture X Size
		ctypes.c_int,					# Texture Y Size
		ctypes.c_float,					# Scale Length
		ctypes.c_int,					# Units
		ctypes.POINTER(ctypes.c_ubyte),	# Selected Poly
		ctypes.c_float,					# Target TD (-0.5 = Half, -2.0 = Double)
		ctypes.POINTER(ctypes.c_float),	# Scale Origin Coordinates
		ctypes.c_int,  # Scale Mode (0 - Average, 1 - Each)
		ctypes.POINTER(ctypes.c_float),	# Result
	]
	tdcore.SetTD.restype = None

	bpy.ops.object.mode_set(mode='OBJECT')

	mesh_data = obj.data
	poly_count = len(mesh_data.polygons)

	# Get UV-coordinates
	uv_layer = mesh_data.uv_layers.active.data
	uvs = np.empty(len(uv_layer) * 2, dtype=np.float32)
	uv_layer.foreach_get("uv", uvs)
	uvs = uvs.reshape(-1, 2).flatten()

	# Get Geometry Area
	areas = calculate_geometry_areas_cpp(obj)

	# Get Vertex Count (per poly)
	vertex_count = np.empty(poly_count, dtype=np.int32)
	mesh_data.polygons.foreach_get("loop_total", vertex_count)

	# --- Scale Origin ---
	origin_coordinates = np.array([scale_origin_co[0], scale_origin_co[1]], dtype=np.float32)
	result = np.zeros_like(uvs, dtype=np.float32)

	tdcore.SetTD(
		uvs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		uvs.size,
		areas.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		vertex_count.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
		poly_count,
		texture_size_x,
		texture_size_y,
		bpy.context.scene.unit_settings.scale_length,
		int(td.units),
		selected_polygons.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
		target_td,
		origin_coordinates.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
		scale_mode,
		result.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
	)

	# --- Change UV ---
	for i, loop in enumerate(mesh_data.loops):
		uv_layer[loop.index].uv.x = result[i * 2]
		uv_layer[loop.index].uv.y = result[i * 2 + 1]

	bpy.ops.object.mode_set(mode=start_mode)

	free_td_core_dll(tdcore)


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
		raise OSError("Unsupported OS")

	addon_path = os.path.dirname(os.path.abspath(__file__))
	tdcore_path = os.path.join(addon_path, lib_name)

	if not os.path.isfile(tdcore_path):
		raise FileNotFoundError(f"Library not found: {tdcore_path}")

	try:
		if sys.platform.startswith("win"):
			return ctypes.WinDLL(tdcore_path)  # Windows
		else:
			return ctypes.CDLL(tdcore_path)  # Linux/macOS
	except OSError as e:
		raise OSError(f"Failed to load library: {tdcore_path}") from e


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