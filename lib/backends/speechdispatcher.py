# -*- coding: utf-8 -*-
from base import ThreadedTTSBackend
import locale, os
import speechd

def getSpeechDSpeaker():
	try:
		return speechd.Speaker('XBMC', 'XBMC')
	except:
		try:
			socket_path = os.path.expanduser('~/.speech-dispatcher/speechd.sock')
			return speechd.Speaker('XBMC', 'XBMC',socket_path=socket_path)
		except:
			pass
	return None
	
class SpeechDispatcherTTSBackend(ThreadedTTSBackend):
	"""Supports The speech-dispatcher on linux"""

	provider = 'Speech-dispatcher'
	displayName = 'Speech Dispatcher'
	interval = 100

	def __init__(self):
		self.connect()
		self.threadedInit()

	def connect(self):
		self.speechdObject = getSpeechDSpeaker()
		if not self.speechdObject: return
		try:
			self.speechdObject.set_language(locale.getdefaultlocale()[0][:2])
		except (KeyError,IndexError):
			pass
		self.speechdObject.set_rate(35)

	def threadedSay(self,text,interrupt=False):
		if not self.speechdObject:
			return
		try:
			self.speechdObject.speak(text)
		except speechd.SSIPCommunicationError:
			self.reconnect()
		except AttributeError: #Happens on shutdown
			pass

	def stop(self):
		try:
			self.speechdObject.cancel()
		except speechd.SSIPCommunicationError:
			self.reconnect()
		except AttributeError: #Happens on shutdown
			pass

	def reconnect(self):
		self.close()
		if self.active: self.connect()
			
	def close(self):
		if self.speechdObject: self.speechdObject.close()
		del self.speechdObject
		self.speechdObject = None
		
	@staticmethod
	def available():
		return bool(getSpeechDSpeaker())

