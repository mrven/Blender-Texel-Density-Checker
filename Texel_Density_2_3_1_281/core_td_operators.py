import bpy
import bmesh
import math

def Vector2dMultiple(A, B, C):
	return abs((B[0]- A[0])*(C[1]- A[1])-(B[1]- A[1])*(C[0]- A[0]))


def Vector3dMultiple(A, B, C):
	result = 0
	vectorX = 0
	vectorY = 0
	vectorZ = 0
	
	vectorX = (B[1]- A[1])*(C[2]- A[2])-(B[2]- A[2])*(C[1]- A[1])
	vectorY = -1*((B[0]- A[0])*(C[2]- A[2])-(B[2]- A[2])*(C[0]- A[0]))
	vectorZ = (B[0]- A[0])*(C[1]- A[1])-(B[1]- A[1])*(C[0]- A[0])
	
	result = math.sqrt(math.pow(vectorX, 2) + math.pow(vectorY, 2) + math.pow(vectorZ, 2))
	return result


def SyncUVSelection():
	mesh = bpy.context.active_object.data
	bm = bmesh.from_edit_mesh(mesh)
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active
	uv_selected_faces = []
	face_count = len(bm.faces)

	for faceid in range (face_count):
		face_is_selected = True
		for loop in bm.faces[faceid].loops:
			if not(loop[uv_layer].select):
				face_is_selected = False
	
		if face_is_selected and bm.faces[faceid].select:
			uv_selected_faces.append(faceid)
	
	for faceid in range (face_count):
		for loop in bm.faces[faceid].loops:
			loop[uv_layer].select = False

	for faceid in uv_selected_faces:
		for loop in bm.faces[faceid].loops:
			loop[uv_layer].select = True

	for face in bm.faces:
		if bpy.context.scene.td.selected_faces:
			face.select_set(False)
		else:
			face.select_set(True)
	    
	for id in uv_selected_faces:
		bm.faces[id].select_set(True)

	bmesh.update_edit_mesh(mesh, False, False)


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

		aspectRatio = textureSizeCurX / textureSizeCurY;
		if aspectRatio < 1:
			aspectRatio = 1 / aspectRatio
		largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;

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
					SyncUVSelection()

				#Get selected list of selected polygons
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(bpy.context.active_object.data.polygons)
				selected_faces = []
				for faceid in range (0, face_count):
					if bpy.context.active_object.data.polygons[faceid].select == True:
						selected_faces.append(faceid)
				
				#get bmesh from active object		
				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()
				for x in selected_faces:
					#set default values for multiplication of vectors (uv and physical area of object)
					localArea = 0
					#UV Area calculating
					#get uv-coordinates of verteces of current triangle
					for trisIndex in range(0, len(bm.faces[x].loops) - 2):
						loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
						loopB = bm.faces[x].loops[trisIndex + 1][bm.loops.layers.uv.active].uv
						loopC = bm.faces[x].loops[trisIndex + 2][bm.loops.layers.uv.active].uv
						#get multiplication of vectors of current triangle
						multiVector = Vector2dMultiple(loopA, loopB, loopC)
						#Increment area of current tri to total uv area
						localArea += 0.5 * multiVector

					gmArea += bpy.context.active_object.data.polygons[x].area
					Area += localArea

				#delete duplicated object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.delete()

		#Calculate TD and Display Value
		if Area > 0:
			#UV Area in percents
			UVspace = Area * 100
			
			#TexelDensity calculating from selected in panel texture size
			if gmArea > 0:
				TexelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length
			else:
				TexelDensity = 0.001

			#show calculated values on panel
			td.uv_space = '%.3f' % round(UVspace, 3) + ' %'
			if td.units == '0':
				td.density = '%.3f' % round(TexelDensity, 3)
			if td.units == '1':
				td.density = '%.3f' % round(TexelDensity*100, 3)
			if td.units == '2':
				td.density = '%.3f' % round(TexelDensity*2.54, 3)
			if td.units == '3':
				td.density = '%.3f' % round(TexelDensity*30.48, 3)

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
			densityNewValue = float(destiny_set_filtered)
			if densityNewValue < 0.0001:
				densityNewValue = 0.0001
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
				for faceid in range (0, len(o.data.polygons)):
					if bpy.context.active_object.data.polygons[faceid].select == True:
						start_selected_faces.append(faceid)

				bpy.ops.object.mode_set(mode='EDIT')

				#If Set TD from UV Editor sync selection
				if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
					SyncUVSelection()

				#Select All Polygons if Calculate TD per Object
				if start_mode == 'OBJECT' or td.selected_faces == False:	
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')

				#Get current TD Value from object or faces
				bpy.ops.object.texel_density_check()
				densityCurrentValue = float(td.density)
				if densityCurrentValue < 0.0001:
					densityCurrentValue = 0.0001

				scaleFac = densityNewValue/densityCurrentValue
				#check opened image editor window
				IE_area = 0
				flag_exist_area = False
				for area in range(len(bpy.context.screen.areas)):
					if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
						IE_area = area
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
				
				bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
				if td.set_method == '0':
					bpy.ops.uv.average_islands_scale()
				bpy.context.area.type = 'VIEW_3D'
				
				if flag_exist_area == True:
					bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'

				bpy.ops.mesh.select_all(action='DESELECT')

				bpy.ops.object.mode_set(mode='OBJECT')
				for faceid in start_selected_faces:
					bpy.context.active_object.data.polygons[faceid].select = True

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