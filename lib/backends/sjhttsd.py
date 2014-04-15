# -*- coding: utf-8 -*-
import audio
import base
import urllib, urllib2
from lib import util

class SJHttsdTTSBackend(base.SimpleTTSBackendBase):
	provider = 'ttsd'
	displayName = 'Local HTTP TTS Server'
	interval = 100
	settings = {	'voice':	None,
					'speed':	0,
					'host':		'127.0.0.1',
					'port':		8256,
					'player':	None
	}

	def __init__(self):
		preferred = self.setting('player') or None
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler,preferred=preferred)
		base.SimpleTTSBackendBase.__init__(self,player)
		self.voice = self.setting('voice')
		self.speed = self.setting('speed')
		self.setHTTPURL()
		self.process = None

	def setHTTPURL(self):
		host = self.setting('host')
		port = self.setting('port')
		if host and port:
			self.httphost = 'http://{0}:{1}/'.format(host,port)
		else:
			self.httphost = 'http://127.0.0.1:8256/'
		
	def runCommand(self,text,outFile):
		postdata = {'voice': self.voice, 'rate': self.speed, 'text': text}
		req = urllib2.Request(self.httphost + 'speak.wav', urllib.urlencode(postdata))
		with open(outFile, "w") as wav:
			try:
				wav.write(urllib2.urlopen(req).read())
			except:
				util.ERROR('SJHttsdTTSBackend: wav.write',hide_tb=True)

	def update(self):
		self.voice = self.setting('voice')
		self.speed = self.setting('speed')
		self.setPlayer(self.setting('player'))
		self.setHTTPURL()

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	def voices(self):
		return urllib2.urlopen(self.httphost + 'voices').read().splitlines()
		
	@staticmethod
	def available():
		return True

