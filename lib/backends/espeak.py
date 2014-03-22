# -*- coding: utf-8 -*-
from base import TTSBackendBase, WavFileTTSBackendBase
import subprocess
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
	displayName = 'eSpeak'
	interval = 100
	def __init__(self):
		libname = ctypes.util.find_library('espeak')
		self.eSpeak = ctypes.cdll.LoadLibrary(libname)
		self.eSpeak.espeak_Initialize(0,0,None,0)
		self.voice = self.userVoice()
		
	def say(self,text,interrupt=False):
		if not self.eSpeak: return
		if self.voice: self.eSpeak.espeak_SetVoiceByName(self.voice)
		if interrupt: self.eSpeak.espeak_Cancel()
		if isinstance(text,unicode): text = text.encode('utf-8')
		sb_text = ctypes.create_string_buffer(text)
		size = ctypes.sizeof(sb_text)
		self.eSpeak.espeak_Synth(sb_text,size,0,0,0,0x1000,None,None)

	def update(self,voice,speed):
		if voice: self.voice = voice
		
	def stop(self):
		if not self.eSpeak: return
		self.eSpeak.espeak_Cancel()
		
	def close(self):
		if not self.eSpeak: return
		self.eSpeak.espeak_Terminate()
		#ctypes.cdll.LoadLibrary('libdl.so').dlclose(self.eSpeak._handle)
		del self.eSpeak
		self.eSpeak = None
		
		
		
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

class ESpeak_XA_TTSBackend(WavFileTTSBackendBase):
	provider = 'eSpeak-XA'
	displayName = 'eSpeak (XBMC Audio)'
	interval = 50
	
	def __init__(self):
		WavFileTTSBackendBase.__init__(self)
		self.voice = self.userVoice()
		self.speed = self.userSpeed()
		
	def runCommand(self,text):
		args = ['espeak','-w',self.outFile]
		if self.voice: args += ['-v',self.voice]
		if self.speed: args += ['-s',str(self.speed)]
		args.append(text)
		subprocess.call(args)			
			
	def update(self,voice,speed):
		if voice: self.voice = voice
		if speed: self.speed = speed
		
	def voices(self):
		import re
		ret = []
		out = subprocess.check_output(['espeak','--voices']).splitlines()
		out.pop(0)
		for l in out:
			ret.append(re.split('\s+',l.strip(),5)[3])
		return ret
		
	@staticmethod
	def available():
		try:
			subprocess.call(['espeak','--help'])
		except:
			return False
		return True
