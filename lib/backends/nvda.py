# -*- coding: utf-8 -*-
import os, xbmc, ctypes
from lib import util
from base import TTSBackendBase

DLL_PATH = os.path.join(xbmc.translatePath(util.info('path')).decode('utf-8'),'lib','backends','nvda','nvdaControllerClient32.dll')

try:
	from ctypes import windll
except ImportError:
	windll =None

class NVDATTSBackend(TTSBackendBase):
	provider = 'nvda'
	displayName = 'NVDA'

	@staticmethod
	def available():
		if not windll:
			return False
		try:
			handle = ctypes.windll.kernel32.LoadLibraryA(DLL_PATH)
			dll = ctypes.windll.LoadLibrary(DLL_PATH)
			res = dll.nvdaController_testIfRunning() == 0
			del dll
			ctypes.windll.kernel32.FreeLibrary(handle)
			return res
		except:
			return False

	def __init__(self):
		try:
			self.handle = ctypes.windll.kernel32.LoadLibraryA(DLL_PATH)
			self.dll = ctypes.windll.LoadLibrary(DLL_PATH)
		except:
			self.handle = None
			self.dll =None

	def say(self,text,interrupt=False):
		if not self.dll:
			return
		if interrupt:
			self.stop()
		self.dll.nvdaController_speakText(text)

	def stop(self):
		self.dll.nvdaController_cancelSpeech()
		
	def close(self):
		del self.dll
		ctypes.windll.kernel32.FreeLibrary(self.handle)

