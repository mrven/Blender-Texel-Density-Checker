import bpy
import bmesh
import math
import colorsys

def Vector2d_Multiply(a, b, c):
	return abs((b[0]- a[0])*(c[1]- a[1])-(b[1]- a[1])*(c[0]- a[0]))


#Deprecated
def Vector3d_Multiply(a, b, c):
	result = 0
	vector_x = 0
	vector_y = 0
	vector_z = 0
	
	vector_x = (b[1]- a[1])*(c[2]- a[2])-(b[2]- a[2])*(c[1]- a[1])
	vector_y = -1*((b[0]- a[0])*(c[2]- a[2])-(b[2]- a[2])*(c[0]- a[0]))
	vector_z = (b[0]- a[0])*(c[1]- a[1])-(b[1]- a[1])*(c[0]- a[0])
	
	result = math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2) + math.pow(vector_z, 2))
	return result


def Value_To_Color(value, range_min, range_max):
	remaped_value = (value - range_min) / (range_max - range_min)
	remaped_value = Saturate(remaped_value)
	hue = (1 - remaped_value) * 0.67
	color = colorsys.hsv_to_rgb(hue, 1, 1)
	color4 = (color[0], color[1], color[2], 1)
	return color4


def Sync_UV_Selection():
	mesh = bpy.context.active_object.data
	bm = bmesh.from_edit_mesh(mesh)
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active
	uv_selected_faces = []
	face_count = len(bm.faces)

	for face_id in range (face_count):
		face_is_selected = True
		for loop in bm.faces[face_id].loops:
			if not(loop[uv_layer].select):
				face_is_selected = False
	
		if face_is_selected and bm.faces[face_id].select:
			uv_selected_faces.append(face_id)
	
	for face_id in range (face_count):
		for loop in bm.faces[face_id].loops:
			loop[uv_layer].select = False

	for face_id in uv_selected_faces:
		for loop in bm.faces[face_id].loops:
			loop[uv_layer].select = True

	for face in bm.faces:
		if bpy.context.scene.td.selected_faces:
			face.select_set(False)
		else:
			face.select_set(True)
	    
	for face_id in uv_selected_faces:
		bm.faces[face_id].select_set(True)

	bmesh.update_edit_mesh(mesh, False, False)


def Calculate_TD_To_List():
	td = bpy.context.scene.td
	calculated_obj_td = []

	#save current mode and active object
	start_active_obj = bpy.context.active_object
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

	bpy.ops.object.mode_set(mode='OBJECT')

	face_count = len(bpy.context.active_object.data.polygons)

	#Duplicate and Triangulate Object
	bpy.ops.object.duplicate()
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

	aspect_ratio = texture_size_cur_x / texture_size_cur_y;
	if aspect_ratio < 1:
		aspect_ratio = 1 / aspect_ratio
	largest_side = texture_size_cur_x if texture_size_cur_x > texture_size_cur_y else texture_size_cur_y;

	#get bmesh from active object		
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	bm.faces.ensure_lookup_table()
	
	for x in range(0, face_count):
		area = 0
		#UV Area calculating
		#get uv-coordinates of verteces of current triangle
		for tri_index in range(0, len(bm.faces[x].loops) - 2):
			loop_a = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
			loop_b = bm.faces[x].loops[tri_index + 1][bm.loops.layers.uv.active].uv
			loop_c = bm.faces[x].loops[tri_index + 2][bm.loops.layers.uv.active].uv
			#get multiplication of vectors of current triangle
			multi_vector = Vector2d_Multiply(loop_a, loop_b, loop_c)
			#Increment area of current tri to total uv area
			area += 0.5 * multi_vector

		gm_area = bpy.context.active_object.data.polygons[x].area

		#TexelDensity calculating from selected in panel texture size
		if gm_area > 0 and area > 0:
			texel_density = ((largest_side / math.sqrt(aspect_ratio)) * math.sqrt(area))/(math.sqrt(gm_area)*100) / bpy.context.scene.unit_settings.scale_length
		else:
			texel_density = 0.001

		#show calculated values on panel
		if td.units == '0':
			texel_density = '%.3f' % round(texel_density, 3)
		if td.units == '1':
			texel_density = '%.3f' % round(texel_density*100, 3)
		if td.units == '2':
			texel_density = '%.3f' % round(texel_density*2.54, 3)
		if td.units == '3':
			texel_density = '%.3f' % round(texel_density*30.48, 3)

		calculated_obj_td.append(float(texel_density))

	#delete duplicated object
	bpy.ops.object.mode_set(mode='OBJECT')
	
	bpy.ops.object.delete()
	bpy.context.view_layer.objects.active = start_active_obj
	
	bpy.ops.object.mode_set(mode=start_mode)

	return calculated_obj_td


def Calculate_UV_Space_To_List():
	td = bpy.context.scene.td
	calculated_obj_uv_space = []

	#save current mode and active object
	start_active_obj = bpy.context.active_object
	start_mode = bpy.context.object.mode

	#set default values
	area=0
	
	bpy.ops.object.mode_set(mode='OBJECT')

	face_count = len(bpy.context.active_object.data.polygons)

	#Duplicate and Triangulate Object
	bpy.ops.object.duplicate()
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

	#get bmesh from active object		
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	bm.faces.ensure_lookup_table()
	
	for x in range(0, face_count):
		area = 0
		#UV Area calculating
		#get uv-coordinates of verteces of current triangle
		for tri_index in range(0, len(bm.faces[x].loops) - 2):
			loop_a = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
			loop_b = bm.faces[x].loops[tri_index + 1][bm.loops.layers.uv.active].uv
			loop_c = bm.faces[x].loops[tri_index + 2][bm.loops.layers.uv.active].uv
			#get multiplication of vectors of current triangle
			multi_vector = Vector2d_Multiply(loop_a, loop_b, loop_c)
			#Increment area of current tri to total uv area
			area += 0.5 * multi_vector

		calculated_obj_uv_space.append(area)

	#delete duplicated object
	bpy.ops.object.mode_set(mode='OBJECT')
	
	bpy.ops.object.delete()
	bpy.context.view_layer.objects.active = start_active_obj
	
	bpy.ops.object.mode_set(mode=start_mode)

	return calculated_obj_uv_space


def Saturate(val):
	return max(min(val, 1), 0)