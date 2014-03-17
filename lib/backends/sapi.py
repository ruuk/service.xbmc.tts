# -*- coding: utf-8 -*-
import sys
from base import TTSBackendBase

class SAPITTSBackend(TTSBackendBase):
	provider = 'SAPI'
	interval = 100
	def __init__(self):
		import comtypes.client
		self.voice = comtypes.client.CreateObject("SAPI.SpVoice")
		voice = self.currentVoice()
		if voice: self.setVoice(voice)
		
	def say(self,text,interrupt=False):
		if interrupt:
			self.voice.Speak(text,3)
		else:
			self.voice.Speak(text,1)
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')

	def stop(self):
		self.voice.Speak('',3)

	def voices(self):
		voices=[]
		v=self.voice.getVoices()
		for i in xrange(len(v)):
			try:
				name=v[i].GetDescription()
			except COMError:
				pass
			voices.append(name)
		return voices

	def setVoice(self,value):
		v=self.voice.getVoices()
		for i in xrange(len(v)):
			voice=v[i]
			if value==voice.GetDescription():
				break
		else:
			# Voice not found.
			return
		self.voice.voice = voice
