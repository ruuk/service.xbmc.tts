# -*- coding: utf-8 -*-
from base import TTSBackendBase
import locale
import speechd

class SpeechDispatcherTTSBackend(TTSBackendBase):
	"""Supports The speech-dispatcher on linux"""

	provider = 'Speech-dispatcher'
	interval = 100

	def __init__(self):
		try:
			self.speechdObject = speechd.Speaker('XBMC', 'XBMC')
		except:
			self.speechdObject =None 
			return
		try:
			self.speechdObject.set_language(locale.getdefaultlocale()[0][:2])
		except (KeyError,IndexError):
			pass
		self.speechdObject.set_rate(50)

	def say(self,text,interrupt=False):
		if not self.speechdObject:
			return
		if interrupt:
			self.speechdObject.cancel()
		self.speechdObject.speak(text.decode('utf8'))

	@staticmethod
	def available():
		try:
			speechdObject = speechd.Speaker('XBMC', 'XBMC')
		except:
			return False
		return True

	def close(self):
		self.speechdObject.close()
		self.speechdObject =None

