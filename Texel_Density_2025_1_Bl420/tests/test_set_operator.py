import bpy
import unittest
from .. import utils

class TestTexelDensitySetOperator(unittest.TestCase):
	# Тест кейсы:
	# • в обжект моде 3д вью
	# • в эдит моде 3д вью с/без селектед фейсес
	# • в юв эдиторе с/без синком выделения
	# • в юв эдиторе с/без селектед фейсес
	# • кейсы, когда полигоны не выделены
	# • кейсы, когда нет юв
	# • кейсы, когда юв маленькое
	# • кейсы с несколькими мешами в обжект и эдит моде
	# • кейсы со сменой размера текстур
	# • кейсы со сменой юнитов
	# • кейс, когда нет активного объекта

	#  Лучше всего тесты держать атомарными и делать по одной проверке в функции, чтобы не повышать сложность тестов

	@classmethod
	def setUpClass(cls):
		print("\n----Starting Texel Density Set Test Suite...----")

	@classmethod
	def tearDownClass(cls):
		print("----Finished Texel Density Set Test Suite...----")

	# All Tests start in object mode
	def setUp(self):
		print(f"Current backend: {utils.get_preferences().calculation_backend}")

		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass

		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		# Added UV Sphere
		bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(2, 0, 0), scale=(2, 2, 2))
		self.sphere = bpy.context.active_object

		# Added Cube
		bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 2, 1))
		self.cube = bpy.context.active_object

		bpy.ops.object.mode_set(mode='OBJECT')

	# All Tests finish clean up and return to object mode
	def tearDown(self):
		# Always return to Object Mode
		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass

		# Clean up scene
		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		print(" ")

	# TD Set Single Selected Object in Object Mode
	def test_set_object_mode(self):
		print("----Run Test TD Set (in Object Mode)----")

		area = bpy.context.area
		if not area:
			self.fail("Failed get area")

		if area.type != 'VIEW_3D':
			original_type = area.type
			area.type = 'VIEW_3D'
		else:
			original_type = None

		td = bpy.context.scene.td
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = self.cube
		bpy.context.view_layer.objects.active.select_set(True)

		expected_density = '1.280'
		expected_uv_space = '250.0000'

		for i in range(3):  # Three times check for 1.28
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '1.28'

					result = bpy.ops.texel_density.set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		expected_density = '5.120'
		expected_uv_space = '4000.0000'

		for i in range(3):  # Three times check for 5.12
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '5.12'

					result = bpy.ops.texel_density.set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		if original_type:
			area.type = original_type

	# TD Set Single Selected Object in Edit Mode
	def test_set_edit_mode(self):
		print("----Run Test TD Set (in Edit Mode)----")

		area = bpy.context.area
		if not area:
			self.fail("Failed get area")

		if area.type != 'VIEW_3D':
			original_type = area.type
			area.type = 'VIEW_3D'
		else:
			original_type = None

		td = bpy.context.scene.td

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = self.cube
		bpy.context.view_layer.objects.active.select_set(True)

		obj = bpy.context.active_object

		td.density = ''
		td.uv_space = ''

		density_value_set = {
			0: '0.64',
			1: '1.28',
			2: '2.56',
			3: '5.12',
			4: '0.64',
			5: '2.56',
		}

		expected_results = {
			0: ('0.640', '12.5000'),
			1: ('1.280', '25.0000'),
			2: ('2.560', '200.0000'),
			3: ('5.120', '400.0000'),
			4: ('0.640', '12.5000'),
			5: ('2.560', '200.0000'),
		}

		total_faces = len(obj.data.polygons)

		for i in range(total_faces):
			with self.subTest(face=i):
				try:
					td.density_set = density_value_set[i]
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')

					bpy.ops.object.mode_set(mode='OBJECT')
					obj.data.polygons[i].select = True

					bpy.ops.object.mode_set(mode='EDIT')
					result = bpy.ops.texel_density.set()

					actual_density = td.density
					actual_uv_space = td.uv_space

					print(f"[Face {i}] Density = {actual_density}, UV Space = {actual_uv_space} %")

					bpy.ops.object.mode_set(mode='OBJECT')

					self.assertIn('FINISHED', result)
					self.assertEqual(actual_density, expected_results[i][0], f"Density mismatch on face {i}")
					self.assertEqual(actual_uv_space, expected_results[i][1], f"UV Space mismatch on face {i}")
				except Exception as e:
					self.fail(f"Test failed on face {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		if original_type:
			area.type = original_type

	# Base Check for Py Backend
	def test_set_py_back(self):
		print("----Run Test Base Check for TD Set for Py Backend----")

		utils.get_preferences().calculation_backend = 'PY'
		print(f"Backend switched to Py. Current is: {utils.get_preferences().calculation_backend}")

		area = bpy.context.area
		if not area:
			self.fail("Failed get area")

		if area.type != 'VIEW_3D':
			original_type = area.type
			area.type = 'VIEW_3D'
		else:
			original_type = None

		td = bpy.context.scene.td
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = self.cube
		bpy.context.view_layer.objects.active.select_set(True)

		expected_density = '1.280'
		expected_uv_space = '250.0000'

		for i in range(3):  # Three times check for 1.28
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '1.28'

					result = bpy.ops.texel_density.set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		expected_density = '5.120'
		expected_uv_space = '4000.0000'

		for i in range(3):  # Three times check for 5.12
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '5.12'

					result = bpy.ops.texel_density.set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		utils.get_preferences().calculation_backend = 'CPP'
		print(f"Backend switched to CPP. Current is: {utils.get_preferences().calculation_backend}")

		if original_type:
			area.type = original_type

def run():
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTexelDensitySetOperator)
	runner = unittest.TextTestRunner()
	runner.run(suite)