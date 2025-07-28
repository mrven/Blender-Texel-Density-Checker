import ctypes
import os
import sys

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

	tdcore.ValueToColor.argtypes = [
		ctypes.POINTER(ctypes.c_float),  # Values
		ctypes.c_int,  # Values Count
		ctypes.c_float,  # Range Min
		ctypes.c_float,  # Range Max
		ctypes.POINTER(ctypes.c_float)  # Results
	]

	tdcore.ValueToColor.restype = None

def free_td_core_dll():
	if not tdcore or not hasattr(tdcore, '_handle'):
		return

	try:
		handle = ctypes.c_void_p(tdcore._handle)

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
		del tdcore