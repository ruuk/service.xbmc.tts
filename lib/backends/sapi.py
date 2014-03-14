# -*- coding: utf-8 -*-
import sys
from base import TTSBackendBase

class SAPITTSBackend(TTSBackendBase):
	provider = 'SAPI'
	interval = 100
	def __init__(self):
		import comtypes.client
		self.voice = comtypes.client.CreateObject("SAPI.SpVoice")
		
	def say(self,text,interrupt=False):
		if interrupt:
			self.voice.Speak(text.decode('utf8'),3)
		else:
			self.voice.Speak(text.decode('utf8'),1)
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')
