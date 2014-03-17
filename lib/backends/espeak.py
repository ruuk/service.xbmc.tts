# -*- coding: utf-8 -*-
from base import TTSBackendBase
import ctypes
import ctypes.util
import os

class espeak_VOICE(ctypes.Structure):
	_fields_=[
		('name',ctypes.c_char_p),
		('languages',ctypes.c_char_p),
		('identifier',ctypes.c_char_p),
		('gender',ctypes.c_byte),
		('age',ctypes.c_byte),
		('variant',ctypes.c_byte),
		('xx1',ctypes.c_byte),
		('score',ctypes.c_int),
		('spare',ctypes.c_void_p),
	]

class ESpeakTTSBackend(TTSBackendBase):
	provider = 'eSpeak'
	interval = 100
	def __init__(self):
		libname = ctypes.util.find_library('espeak')
		self.eSpeak = ctypes.cdll.LoadLibrary(libname)
		self.eSpeak.espeak_Initialize(0,0,None,0)
		
	def say(self,text,interrupt=False):
		voice = self.currentVoice()
		if voice: self.eSpeak.espeak_SetVoiceByName(voice)
		if interrupt: self.eSpeak.espeak_Cancel()
		if isinstance(text,unicode): text = text.encode('utf-8')
		sb_text = ctypes.create_string_buffer(text)
		size = ctypes.sizeof(sb_text)
		self.eSpeak.espeak_Synth(sb_text,size,0,0,0,0x1000,None,None)

	def stop(self):
		self.eSpeak.espeak_Cancel()
		
	def close(self):
		self.eSpeak.espeak_Cancel()
		self.eSpeak.espeak_Terminate()
		
	@staticmethod
	def available():
		return bool(ctypes.util.find_library('espeak'))

	def voices(self):
		voices=self.eSpeak.espeak_ListVoices(None)
		aespeak_VOICE=ctypes.POINTER(ctypes.POINTER(espeak_VOICE))
		pvoices=ctypes.cast(voices,aespeak_VOICE)
		voiceList=[]
		index=0
		while pvoices[index]:
			voiceList.append(os.path.basename(pvoices[index].contents.identifier))
			index+=1
		return voiceList

