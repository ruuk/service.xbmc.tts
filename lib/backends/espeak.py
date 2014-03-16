# -*- coding: utf-8 -*-
from base import TTSBackendBase
import ctypes
import ctypes.util

class ESpeakTTSBackend(TTSBackendBase):
	provider = 'eSpeak'
	interval = 100
	def __init__(self):
		libname = ctypes.util.find_library('espeak')
		self.eSpeak = ctypes.cdll.LoadLibrary(libname)
		self.eSpeak.espeak_Initialize(0,0,None,0)
		
	def say(self,text,interrupt=False):
		if interrupt: self.eSpeak.espeak_Cancel()
		if isinstance(text,unicode): text = text.encode('utf-8')
		sb_text = ctypes.create_string_buffer(text)
		size = ctypes.sizeof(sb_text)
		self.eSpeak.espeak_Synth(text,size,0,0,0,0x1000,None,None)

	def stop(self):
		self.eSpeak.espeak_Cancel()
		
	def close(self):
		self.eSpeak.espeak_Cancel()
		self.eSpeak.espeak_Terminate()
		
	@staticmethod
	def available():
		return bool(ctypes.util.find_library('espeak'))