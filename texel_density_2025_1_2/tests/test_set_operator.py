import bpy
import unittest
from .. import utils

class TestTexelDensitySetOperator(unittest.TestCase):
	# Test cases:
	# • In object mode with 3d view
	# • In edit mode with 3d view with/without selected faces
	# • In uv editor with/without sync selection
	# • In uv editor with/without selected faces
	# • Cases when polygons are not selected
	# • Cases when there is no uv
	# • Cases when uv is small
	# • Cases with multiple meshes in object and edit mode
	# • Cases with changing texture size
	# • Cases with changing units
	# • Case when there is no active object

	# It is better to keep tests atomic and make one check per function, so that the complexity of tests does not increase

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

		expected_density = 1.28
		expected_uv_space = 250

		for i in range(3):  # Three times check for 1.28
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '1.28'

					result = bpy.ops.object.texel_density_set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					assert_float_equal_percentage(self, float(td.density), expected_density, 5)
					assert_float_equal_percentage(self, float(td.uv_space), expected_uv_space, 10)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		expected_density = 5.12
		expected_uv_space = 4000

		for i in range(3):  # Three times check for 5.12
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '5.12'

					result = bpy.ops.object.texel_density_set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					assert_float_equal_percentage(self, float(td.density), expected_density, 5)
					assert_float_equal_percentage(self, float(td.uv_space), expected_uv_space, 10)
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
			0: (0.64, 12.5),
			1: (1.28, 25),
			2: (2.56, 200),
			3: (5.12, 400),
			4: (0.64, 12.5),
			5: (2.56, 200),
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
					result = bpy.ops.object.texel_density_set()

					actual_density = td.density
					actual_uv_space = td.uv_space

					print(f"[Face {i}] Density = {actual_density}, UV Space = {actual_uv_space} %")

					bpy.ops.object.mode_set(mode='OBJECT')

					self.assertIn('FINISHED', result)
					assert_float_equal_percentage(self, float(td.density), expected_results[i][0], 5, f"Density mismatch on face {i}")
					assert_float_equal_percentage(self, float(td.uv_space), expected_results[i][1], 10, f"UV Space mismatch on face {i}")
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

		expected_density = 1.28
		expected_uv_space = 250

		for i in range(3):  # Three times check for 1.28
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '1.28'

					result = bpy.ops.object.texel_density_set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					assert_float_equal_percentage(self, float(td.density), expected_density, 5)
					assert_float_equal_percentage(self, float(td.uv_space), expected_uv_space, 10)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		expected_density = 5.12
		expected_uv_space = 4000

		for i in range(3):  # Three times check for 5.12
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '5.12'

					result = bpy.ops.object.texel_density_set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					assert_float_equal_percentage(self, float(td.density), expected_density, 5)
					assert_float_equal_percentage(self, float(td.uv_space), expected_uv_space, 10)
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


def assert_float_equal_percentage(self, a, b, percent_threshold: float, msg=None):
	if b == 0.0:
		self.assertEqual(a, b, msg or f"Cannot compare to zero reference: a={a}, b={b}")
	else:
		diff_percent = abs((a - b) / b) * 100.0
		self.assertLessEqual(diff_percent, percent_threshold,
			msg or f"{a} and {b} differ by {diff_percent:.6f}%, which exceeds allowed {percent_threshold}%")