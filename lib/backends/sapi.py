# -*- coding: utf-8 -*-
import sys
from base import ThreadedTTSBackend

class SAPITTSBackend(ThreadedTTSBackend):
	provider = 'SAPI'
	displayName = 'SAPI (Windows Internal)'
	settings = {'voice':''}
	interval = 100
	def __init__(self):
		import comtypes.client
		self.SpVoice = comtypes.client.CreateObject("SAPI.SpVoice")
		self.update()
		self.threadedInit()
		
	def threadedSay(self,text):
		if not self.SpVoice: return
		self.SpVoice.Speak(text,1)

	def stop(self):
		if not self.SpVoice: return
		self.SpVoice.Speak('',3)

	def voices(self):
		voices=[]
		v=self.SpVoice.getVoices()
		for i in xrange(len(v)):
			try:
				name=v[i].GetDescription()
			except COMError: #analysis:ignore
				pass
			voices.append(name)
		return voices

	def isSpeaking(self):
		return ThreadedTTSBackend.isSpeaking(self) or None
		
	def update(self):
		voice_name = self.setting('voice')
		if voice_name:
			v=self.SpVoice.getVoices()
			for i in xrange(len(v)):
				voice=v[i]
				if voice_name==voice.GetDescription():
					break
			else:
				# Voice not found.
				return
			self.SpVoice.voice = voice
		
	def close(self):
		del self.SpVoice
		self.SpVoice = None
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')