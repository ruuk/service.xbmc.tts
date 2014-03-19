# -*- coding: utf-8 -*-
from base import TTSBackendBase
import locale
import speechd

class SpeechDispatcherTTSBackend(TTSBackendBase):
	"""Supports The speech-dispatcher on linux"""

	provider = 'Speech-dispatcher'
	interval = 100

	def __init__(self):
		self.connect()

	def connect(self):
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
			self.stop()
		try:
			self.speechdObject.speak(text)
		except speechd.SSIPCommunicationError:
			self.close()
			self.connect()

	def stop(self):
		try:
			self.speechdObject.cancel()
		except speechd.SSIPCommunicationError:
			self.close()
			self.connect()

	@staticmethod
	def available():
		try:
			speechdObject = speechd.Speaker('XBMC', 'XBMC')
		except:
			return False
		return True

	def close(self):
		if self.speechdObject: self.speechdObject.close()

