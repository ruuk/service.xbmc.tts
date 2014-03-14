# -*- coding: utf-8 -*-
import os, subprocess, xbmc
from lib import util
from base import TTSBackendBase

class Pico2WaveTTSBackend(TTSBackendBase):
	provider = 'pico2wav'
	def __init__(self):
		import xbmcaddon
		profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
		if not os.path.exists(profile): os.makedirs(profile)
		self.outFile = os.path.join(profile,'speech.wav')
		util.LOG('pico2wave output file: ' + self.outFile)
		
	def say(self,text,interrupt=False):
		if not text: return
		subprocess.call(['pico2wave', '-w', '{0}'.format(self.outFile), '{0}'.format(text)])
		#xbmc.playSFX(self.outFile) #Doesn't work - caches wav
		subprocess.call(['aplay','{0}'.format(self.outFile)])
		
	@staticmethod
	def available():
		try:
			subprocess.call(['pico2wave', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True