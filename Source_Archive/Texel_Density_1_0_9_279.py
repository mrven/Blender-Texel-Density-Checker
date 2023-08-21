bl_info = {
	"name": "Texel Density Checker",
	"description": "Tools for for checking Texel Density and wasting of uv space",
	"author": "Ivan 'mrven' Vostrikov, Toomas Laik",
	"version": (1, 0, 9),
	"blender": (2, 7, 8),
	"location": "3D View > Toolshelf > Texel Density Checker",
	"category": "Object",
}

import bpy
import bmesh
import math

#-------------------------------------------------------
class Texel_Density_Check(bpy.types.Operator):
	"""Check Density"""
	bl_idname = "object.texel_density_check"
	bl_label = "Check Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		message = "TD is calculated"
		#save current mode and active object
		actObj = bpy.context.scene.objects.active
		current_selected_obj = bpy.context.selected_objects
		try:
			actObjType = actObj.type
			start_mode = bpy.context.object.mode
		except:
			actObjType = 'None'
			start_mode = 'OBJECT'
		current_mode = start_mode
		
		#proceed if active object is mesh
		if (actObjType == 'MESH' and len(actObj.data.uv_layers) > 0):
			if (bpy.context.object.mode == 'EDIT') and (context.scene.selected_faces == True):
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				actObj.select = True
				bpy.ops.object.duplicate()
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
				#set default values
				Area=0
				gmArea = 0
				textureSizeCurX = 1024
				textureSizeCurY = 1024
				
				#Get texture size from panel
				if bpy.context.scene.texture_size == '0':
					textureSizeCurX = 512
					textureSizeCurY = 512
				if bpy.context.scene.texture_size == '1':
					textureSizeCurX = 1024
					textureSizeCurY = 1024
				if bpy.context.scene.texture_size == '2':
					textureSizeCurX = 2048
					textureSizeCurY = 2048
				if bpy.context.scene.texture_size == '3':
					textureSizeCurX = 4096
					textureSizeCurY = 4096
				if bpy.context.scene.texture_size == '4':
					try:
						textureSizeCurX = int(context.scene.custom_width)
					except:
						textureSizeCurX = 1024
						message = "Width value is wrong. Height will be set to 1024"
					try:
						textureSizeCurY = int(context.scene.custom_height)
					except:
						textureSizeCurY = 1024
						message = "Height value is wrong. Height will be set to 1024"
				#get bmesh from active object
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(bpy.context.active_object.data.polygons)
				selected_faces = []
				for faceid in range (0, face_count):
					if bpy.context.active_object.data.polygons[faceid].select == True:
						selected_faces.append(faceid)
						
				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()
				for x in selected_faces:
					#set default values for multiplication of vectors (uv and physical area of object)
					multiVector = 0
					gmmultiVector = 0
					#UV Area calculating
					#get uv-coordinates of vertexes of current triangle
					loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
					loopB = bm.faces[x].loops[1][bm.loops.layers.uv.active].uv
					loopC = bm.faces[x].loops[2][bm.loops.layers.uv.active].uv
					#get multiplication of vectors of current triangle
					multiVector = Vector2dMultiple(loopA, loopB, loopC)
					#Increment area of current tri to total uv area
					Area+=0.5*multiVector

					#Phisical Area calculating
					#get world coordinates of vertexes of current triangle
					gmloopA = bm.faces[x].loops[0].vert.co
					gmloopB = bm.faces[x].loops[1].vert.co
					gmloopC = bm.faces[x].loops[2].vert.co
					#get multiplication of vectors of current triangle
					gmmultiVector = Vector3dMultiple(gmloopA, gmloopB, gmloopC)
					#Increment area of current tri to total phisical area
					gmArea += 0.5*gmmultiVector
					
				bpy.ops.object.mode_set(mode='OBJECT')
				
				if len(selected_faces) > 0:
					#UV Area in percents
					UVspace = Area * 100
					
					aspectRatio = textureSizeCurX / textureSizeCurY;
					if aspectRatio < 1:
						aspectRatio = 1 / aspectRatio
					largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;
					#TexelDensity calculating from selected in panel texture size
					TexelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length

					#show calculated values on panel
					context.scene.uv_space = '%.3f' % round(UVspace, 3) + ' %'
					if context.scene.units == '0':
						context.scene.density = '%.3f' % round(TexelDensity, 3)
					if context.scene.units == '1':
						context.scene.density = '%.3f' % round(TexelDensity*100, 3)
					if context.scene.units == '2':
						context.scene.density = '%.3f' % round(TexelDensity*2.54, 3)
					if context.scene.units == '3':
						context.scene.density = '%.3f' % round(TexelDensity*30.48, 3)
				else:
					self.report({'INFO'}, 'No faces selected')
				
				#delete duplicated object
				bpy.ops.object.delete()
				#select saved object
				for x in current_selected_obj:
					x.select = True
				bpy.context.scene.objects.active = actObj
				bpy.ops.object.mode_set(mode='EDIT')
			#--------------------------------------------------
			#Calculating for all mesh
			else:
				#if start mode = edit, change to object mode
				if current_mode == 'EDIT':
					bpy.ops.object.mode_set(mode='OBJECT')
					current_mode = 'OBJECT'
				#Duplicate active object and triangulate mesh
				if current_mode == 'OBJECT':
					bpy.ops.object.select_all(action='DESELECT')
					actObj.select = True
					bpy.ops.object.duplicate()
					bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

				#set default values
				Area=0
				gmArea = 0
				textureSizeCurX = 1024
				textureSizeCurY = 1024
				
				#Get texture size from panel
				if bpy.context.scene.texture_size == '0':
					textureSizeCurX = 512
					textureSizeCurY = 512
				if bpy.context.scene.texture_size == '1':
					textureSizeCurX = 1024
					textureSizeCurY = 1024
				if bpy.context.scene.texture_size == '2':
					textureSizeCurX = 2048
					textureSizeCurY = 2048
				if bpy.context.scene.texture_size == '3':
					textureSizeCurX = 4096
					textureSizeCurY = 4096
				if bpy.context.scene.texture_size == '4':
					try:
						textureSizeCurX = int(context.scene.custom_width)
					except:
						textureSizeCurX = 1024
						message = "Width value is wrong. Height will be set to 1024"
					try:
						textureSizeCurY = int(context.scene.custom_height)
					except:
						textureSizeCurY = 1024
						message = "Height value is wrong. Height will be set to 1024"
				
				#get bmesh from active object
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()

				#get faces and round this
				face_count = len(bm.faces)
				for faceid in range (0, face_count):
					#set default values for multiplication of vectors (uv and physical area of object)
					multiVector = 0
					gmmultiVector = 0
					#UV Area calculating
					#get uv-coordinates of vertexes of current triangle
					loopA = bm.faces[faceid].loops[0][bm.loops.layers.uv.active].uv
					loopB = bm.faces[faceid].loops[1][bm.loops.layers.uv.active].uv
					loopC = bm.faces[faceid].loops[2][bm.loops.layers.uv.active].uv
					#get multiplication of vectors of current triangle
					multiVector = Vector2dMultiple(loopA, loopB, loopC)
					#Increment area of current tri to total uv area
					Area+=0.5*multiVector

					#Phisical Area calculating
					#get world coordinates of vertexes of current triangle
					gmloopA = bm.faces[faceid].loops[0].vert.co
					gmloopB = bm.faces[faceid].loops[1].vert.co
					gmloopC = bm.faces[faceid].loops[2].vert.co
					#get multiplication of vectors of current triangle
					gmmultiVector = Vector3dMultiple(gmloopA, gmloopB, gmloopC)
					#Increment area of current tri to total physical area
					gmArea += 0.5*gmmultiVector
					
				#UV Area in percents
				UVspace = Area * 100
				
				aspectRatio = textureSizeCurX / textureSizeCurY;
				if aspectRatio < 1:
					aspectRatio = 1 / aspectRatio
				largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;
				#TexelDensity calculating from selected in panel texture size
				TexelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length
				
				#show calculated values on panel
				context.scene.uv_space = '%.3f' % round(UVspace, 3) + ' %'
				if context.scene.units == '0':
					context.scene.density = '%.3f' % round(TexelDensity, 3)
				if context.scene.units == '1':
					context.scene.density = '%.3f' % round(TexelDensity*100, 3)
				if context.scene.units == '2':
					context.scene.density = '%.3f' % round(TexelDensity*2.54, 3)
				if context.scene.units == '3':
					context.scene.density = '%.3f' % round(TexelDensity*30.48, 3)
				#set object mode and delete duplicated object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.delete()
				#select saved object and return into initial mode
				for x in current_selected_obj:
					x.select = True
				bpy.context.scene.objects.active = actObj
				
				bpy.ops.object.mode_set(mode=start_mode)
			
			self.report({'INFO'}, message)
			
		else:
			
			self.report({'ERROR'}, 'Active object isn''t a mesh or doesn\'t have UV')

		return {'FINISHED'}

#-------------------------------------------------------
class Texel_Density_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.texel_density_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		message = "TD is changed"
		enSetTD = True
		actObj = bpy.context.scene.objects.active
		current_selected_obj = bpy.context.selected_objects
		
		destiny_set_filtered = context.scene.density_set.replace(',', '.')
		
		try:
			bpy.ops.object.texel_density_check()
		except:
			message = "Try Calculate TD before"
			enSetTD = False
		densityCurrentValue = float(context.scene.density)
		try:
			densityNewValue = float(destiny_set_filtered)
		except:
			densityNewValue = densityCurrentValue
			message = "Density value is wrong"
		if enSetTD:
			if (densityNewValue != 0):
				if (bpy.context.object.mode == 'EDIT') and (context.scene.selected_faces == True):
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
					
					if bpy.context.scene.tool_settings.use_uv_select_sync == False:
						bpy.ops.uv.select_all(action = 'SELECT')
					
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					if context.scene.set_method == '0':
						bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					
					bpy.ops.object.texel_density_check()
					
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'

				else:
					scaleFac = densityNewValue/densityCurrentValue
					#check opened image editor window
					IE_area = 0
					flag_exist_area = False
					for area in range(len(bpy.context.screen.areas)):
						if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
							IE_area = area
							flag_exist_area = True
							bpy.context.screen.areas[area].type = 'CONSOLE'
							
					start_mode = bpy.context.object.mode
					
					if start_mode == 'OBJECT':
						bpy.ops.object.mode_set(mode='EDIT')
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					
					bpy.context.area.type = 'IMAGE_EDITOR'
					
					if bpy.context.area.spaces[0].image != None:
						if bpy.context.area.spaces[0].image.name == 'Render Result':
							bpy.context.area.spaces[0].image = None
					
					bpy.ops.uv.select_all(action = 'SELECT')
					
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					if context.scene.set_method == '0':
						bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					bpy.ops.object.mode_set(mode=start_mode)
					
					bpy.ops.object.texel_density_check()
					
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'
			else:
				message = "Density must be greater than 0"
		self.report({'INFO'}, message)
		
		for x in current_selected_obj:
			x.select = True
		bpy.context.scene.objects.active = actObj
				
		return {'FINISHED'}
		
#-------------------------------------------------------
class Texel_Density_Copy(bpy.types.Operator):
	"""Copy Density"""
	bl_idname = "object.texel_density_copy"
	bl_label = "Copy Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		message = "TD is copied"
		enCopyTD = True
		current_selected_obj = bpy.context.selected_objects
		actObj = bpy.context.scene.objects.active
		try:
			bpy.ops.object.texel_density_check()
		except:
			message = "Try Calculate TD before"
			enCopyTD = False
		densitySourceObject = float(context.scene.density)
		
		if enCopyTD:
			for x in current_selected_obj:
				bpy.ops.object.select_all(action='DESELECT')
				if (x.type == 'MESH' and len(x.data.uv_layers) > 0):
					x.select = True
					bpy.context.scene.objects.active = x
					bpy.ops.object.texel_density_check()
					densityCurrentValue = float(context.scene.density)
					scaleFac = densitySourceObject/densityCurrentValue
				
					IE_area = 0
					flag_exist_area = False
					for area in range(len(bpy.context.screen.areas)):
						if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
							IE_area = area
							flag_exist_area = True
							bpy.context.screen.areas[area].type = 'CONSOLE'
					
					bpy.ops.object.mode_set(mode='EDIT')
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					
					bpy.context.area.type = 'IMAGE_EDITOR'
					
					if bpy.context.area.spaces[0].image != None:
						if bpy.context.area.spaces[0].image.name == 'Render Result':
							bpy.context.area.spaces[0].image = None
					
					bpy.ops.uv.select_all(action = 'SELECT')
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					bpy.ops.object.mode_set(mode='OBJECT')
				
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'
		
		for x in current_selected_obj:
			x.select = True
		bpy.context.scene.objects.active = actObj
		
		self.report({'INFO'}, message)
		return {'FINISHED'}

#-------------------------------------------------------
class Calculated_To_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.calculate_to_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.scene.density_set = context.scene.density
		
		return {'FINISHED'}
		
#-------------------------------------------------------
class Preset_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.preset_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	TDValue = bpy.props.StringProperty()
	
	def execute(self, context):
		context.scene.density_set = self.TDValue
		bpy.ops.object.texel_density_set()
				
		return {'FINISHED'}
		
#-------------------------------------------------------
class Select_Same_TD(bpy.types.Operator):
	"""Select Faces with same TD"""
	bl_idname = "object.select_same_texel"
	bl_label = "Select Faces with same TD"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		message = "Faces selected"
		actObj = bpy.context.scene.objects.active
		current_selected_obj = bpy.context.selected_objects
		
		#proceed if active object is mesh
		if (len(actObj.data.uv_layers) > 0):	
			#select mode faces
			bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
			#check number of faces
			selected_faces = 0
			face_count = len(bpy.context.active_object.data.polygons)
			
			bpy.ops.object.mode_set(mode='OBJECT')
			for x in range(0, face_count):
				if bpy.context.active_object.data.polygons[x].select == True:
					selected_faces += 1 
			bpy.ops.object.mode_set(mode='EDIT')
			
			if selected_faces > 1 or selected_faces < 1:
				message = "Select only one faces"
			else:
				selected_faces_mode_state = context.scene.selected_faces
				context.scene.selected_faces = True
				bpy.ops.object.texel_density_check()
				search_td_value = float(context.scene.density)
				
				#proceed if active object is mesh
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				actObj.select = True
				bpy.ops.object.duplicate()
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

				#set default values
				Area=0
				gmArea = 0
				textureSizeCurX = 1024
				textureSizeCurY = 1024

				#Get texture size from panel
				if bpy.context.scene.texture_size == '0':
					textureSizeCurX = 512
					textureSizeCurY = 512
				if bpy.context.scene.texture_size == '1':
					textureSizeCurX = 1024
					textureSizeCurY = 1024
				if bpy.context.scene.texture_size == '2':
					textureSizeCurX = 2048
					textureSizeCurY = 2048
				if bpy.context.scene.texture_size == '3':
					textureSizeCurX = 4096
					textureSizeCurY = 4096
				if bpy.context.scene.texture_size == '4':
					try:
						textureSizeCurX = int(context.scene.custom_width)
					except:
						textureSizeCurX = 1024
						message = "Width value is wrong. Height will be set to 1024"
					try:
						textureSizeCurY = int(context.scene.custom_height)
					except:
						textureSizeCurY = 1024
						message = "Height value is wrong. Height will be set to 1024"

				#Get polygon pool from original geometry
				#face_count = len(bpy.context.active_object.data.polygons)

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
				bpy.ops.mesh.select_all(action='DESELECT')

				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()
				
				searched_faces=[]
				threshold_filtered = context.scene.select_td_threshold.replace(',', '.')
				try:
					threshold_td_value = float(threshold_filtered)
				except:
					threshold_td_value = 0.1
					context.scene.select_td_threshold = "0.1"
				
				for x in range(0, face_count):
					#set default values for multiplication of vectors (uv and physical area of object)
					multiVector = 0
					gmmultiVector = 0
					#UV Area calculating
					#get uv-coordinates of vertexes of current triangle
					loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
					loopB = bm.faces[x].loops[1][bm.loops.layers.uv.active].uv
					loopC = bm.faces[x].loops[2][bm.loops.layers.uv.active].uv
					#get multiplication of vectors of current triangle
					multiVector = Vector2dMultiple(loopA, loopB, loopC)
					#Increment area of current tri to total uv area
					Area=0.5*multiVector

					#Phisical Area calculating
					#get world coordinates of vertexes of current triangle
					gmloopA = bm.faces[x].loops[0].vert.co
					gmloopB = bm.faces[x].loops[1].vert.co
					gmloopC = bm.faces[x].loops[2].vert.co
					#get multiplication of vectors of current triangle
					gmmultiVector = Vector3dMultiple(gmloopA, gmloopB, gmloopC)
					#Increment area of current tri to total physical area
					gmArea = 0.5*gmmultiVector
					
					aspectRatio = textureSizeCurX / textureSizeCurY;
					if aspectRatio < 1:
						aspectRatio = 1 / aspectRatio
					largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;
					#TexelDensity calculating from selected in panel texture size
					TexelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length

					#show calculated values on panel
					if context.scene.units == '0':
						context.scene.density = '%.3f' % round(TexelDensity, 3)
					if context.scene.units == '1':
						context.scene.density = '%.3f' % round(TexelDensity*100, 3)
					if context.scene.units == '2':
						context.scene.density = '%.3f' % round(TexelDensity*2.54, 3)
					if context.scene.units == '3':
						context.scene.density = '%.3f' % round(TexelDensity*30.48, 3)
					
					current_poly_td_value = float(context.scene.density)
					
					if (current_poly_td_value > (search_td_value - threshold_td_value)) and (current_poly_td_value < (search_td_value + threshold_td_value)):
						searched_faces.append(x)
				
				bpy.ops.object.mode_set(mode='OBJECT')
				
				#delete duplicated object
				bpy.ops.object.delete()
				#select saved object
				for x in current_selected_obj:
					x.select = True
				bpy.context.scene.objects.active = actObj
				
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				
				for faceid in searched_faces:
					bpy.context.active_object.data.polygons[faceid].select = True
				bpy.ops.object.mode_set(mode='EDIT')
				
				message = "Faces Selected"
				context.scene.selected_faces = selected_faces_mode_state
		else:
			message = "This object don't have uv"
			
		self.report({'INFO'}, message)
		
		return {'FINISHED'}
		
#-------------------------------------------------------
#FUNCTIONS
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

#-------------------------------------------------------
# Panel 
class VIEW3D_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (context.object is not None)

	def draw(self, context):
		layout = self.layout
		layout.prop(context.scene, 'units', expand=False)
		layout.label("Texture Size:")
		row = layout.row()
		row.prop(context.scene, 'texture_size', expand=False)
		if context.scene.texture_size == '4':
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(percentage=0.85)
			c = split.column()
			c.prop(context.scene, "custom_width")
			split = split.split()
			c = split.column()
			c.label("px")
			#----
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(percentage=0.85)
			c = split.column()
			c.prop(context.scene, "custom_height")
			split = split.split()
			c = split.column()
			c.label("px")
		if context.object.mode == 'EDIT':
			layout.separator()
			layout.prop(context.scene, "selected_faces", text="Selected Faces")
		layout.separator()
		layout.label("Filled UV Space:")
		row = layout.row()
		row.prop(context.scene, "uv_space")
		row.enabled = False
		layout.label("Texel Density:")
		row = layout.row()
		c = row.column()
		row = c.row()
		split = row.split(percentage=0.65)
		c = split.column()
		c.prop(context.scene, "density")
		split = split.split()
		c = split.column()
		if context.scene.units == '0':
			c.label("px/cm")
		if context.scene.units == '1':
			c.label("px/m")
		if context.scene.units == '2':
			c.label("px/in")
		if context.scene.units == '3':
			c.label("px/ft")
		row.enabled = False
		layout.operator("object.texel_density_check", text="Calculate TD")
		layout.operator("object.calculate_to_set", text="Calc -> Set Value")
		layout.separator()
		layout.label("Set Texel Density")
		layout.prop(context.scene, 'set_method', expand=False)
		row = layout.row()
		c = row.column()
		row = c.row()
		split = row.split(percentage=0.65)
		c = split.column()
		c.prop(context.scene, "density_set")
		split = split.split()
		c = split.column()
		if context.scene.units == '0':
			c.label("px/cm")
		if context.scene.units == '1':
			c.label("px/m")
		if context.scene.units == '2':
			c.label("px/in")
		if context.scene.units == '3':
			c.label("px/ft")
		layout.operator("object.texel_density_set", text="Set My TD")
		
		#--Aligner Preset Buttons----
		row = layout.row()
		c = row.column()
		row = c.row()
		split = row.split(percentage=0.33)
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="20.48").TDValue="20.48"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="2048").TDValue="2048"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="52.0192").TDValue="52.0192"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="624.2304").TDValue="624.2304"
		split = split.split(percentage=0.5)
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="10.24").TDValue="10.24"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="1024").TDValue="1024"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="26.0096").TDValue="26.0096"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="312.1152").TDValue="312.1152"
		split = split.split()
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="5.12").TDValue="5.12"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="512").TDValue="512"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="13.0048").TDValue="13.0048"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="156.0576").TDValue="156.0576"
			
		#--Aligner Preset Buttons----
		row = layout.row()
		c = row.column()
		row = c.row()
		split = row.split(percentage=0.33)
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="2.56").TDValue="2.56"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="256").TDValue="256"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="6.5024").TDValue="6.5024"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="78.0288").TDValue="78.0288"
		split = split.split(percentage=0.5)
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="1.28").TDValue="1.28"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="128").TDValue="128"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="3.2512").TDValue="3.2512"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="39.0144").TDValue="39.0144"
		split = split.split()
		c = split.column()
		if context.scene.units == '0':
			c.operator("object.preset_set", text="0.64").TDValue="0.64"
		if context.scene.units == '1':
			c.operator("object.preset_set", text="64").TDValue="64"
		if context.scene.units == '2':
			c.operator("object.preset_set", text="1.6256").TDValue="1.6256"
		if context.scene.units == '3':
			c.operator("object.preset_set", text="19.5072").TDValue="19.5072"
		
		if context.object.mode == 'OBJECT':
			layout.separator()
			layout.operator("object.texel_density_copy", text="TD from Active to Others")
			
		if context.object.mode == 'EDIT':
			layout.separator()
			layout.operator("object.select_same_texel", text="Select Faces with same TD")
			layout.prop(context.scene, "select_td_threshold")
		
#-------------------------------------------------------		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.uv_space = bpy.props.StringProperty(
		name="",
		description="wasting of uv space",
		default="0")
	bpy.types.Scene.density = bpy.props.StringProperty(
		name="",
		description="Texel Density",
		default="0")
	bpy.types.Scene.density_set = bpy.props.StringProperty(
		name="",
		description="Texel Density",
		default="0")
	tex_size = (('0','512px',''),('1','1024px',''),('2','2048px',''),('3','4096px',''), ('4','Custom',''))
	bpy.types.Scene.texture_size = bpy.props.EnumProperty(name="", items = tex_size)
	bpy.types.Scene.selected_faces = bpy.props.BoolProperty(
		name="Selected Faces",
		description="Operate only on selected faces",
		default = False)
	bpy.types.Scene.custom_width = bpy.props.StringProperty(
		name="Width",
		description="Custom Width",
		default="1024")
	bpy.types.Scene.custom_height = bpy.props.StringProperty(
		name="Height",
		description="Custom Height",
		default="1024")
	units_list = (('0','px/cm',''),('1','px/m',''), ('2','px/in',''), ('3','px/ft',''))
	bpy.types.Scene.units = bpy.props.EnumProperty(name="Units", items = units_list)
	bpy.types.Scene.select_td_threshold = bpy.props.StringProperty(
		name="Select Threshold",
		description="Select Threshold",
		default="0.1")
	set_method_list = (('0','Each',''),('1','Average',''))
	bpy.types.Scene.set_method = bpy.props.EnumProperty(name="Set Method", items = set_method_list)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.texture_size
	del bpy.types.Scene.uv_space
	del bpy.types.Scene.density
	del bpy.types.Scene.density_set
	del bpy.types.Scene.selected_faces
	del bpy.types.Scene.custom_width
	del bpy.types.Scene.custom_height
	del bpy.types.Scene.units
	del bpy.types.Scene.select_td_threshold
	del bpy.types.Scene.set_method

if __name__ == "__main__":
	register()