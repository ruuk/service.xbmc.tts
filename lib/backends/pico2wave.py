# -*- coding: utf-8 -*-
import os, subprocess, xbmc
from base import WavFileTTSBackendBase

class Pico2WaveTTSBackend(WavFileTTSBackendBase):
	provider = 'pico2wav'
	displayName = 'pico2wav'
	def __init__(self):
		self.process = None
		self.active = True
		WavFileTTSBackendBase.__init__(self)
		
	def runCommand(self,text):
		subprocess.call(['pico2wave', '-w', '{0}'.format(self.outFile), '{0}'.format(text)])
		
	def play(self):
		self.process = subprocess.Popen(['aplay','{0}'.format(self.outFile)])
		while self.process.poll() == None and self.active: xbmc.sleep(10)
			
	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass
		
	def close(self):
		self.active = False
		
	@staticmethod
	def available():
		try:
			subprocess.call(['pico2wave', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True