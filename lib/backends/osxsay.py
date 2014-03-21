# -*- coding: utf-8 -*-
import xbmc, sys, subprocess
from base import ThreadedTTSBackend

class OSXSayTTSBackend(ThreadedTTSBackend):
	provider = 'OSXSay'
	displayName = 'OSX Say (OSX Internal)'
	interval = 100
	
	def __init__(self):
		self.process = None
		self.threadedInit()
		
	def threadedSay(self,text):
		if not text: return
		self.process = subprocess.Popen(['say', text])
		self.process.wait()
		
	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	@staticmethod
	def available():
		return sys.platform == 'darwin' and not xbmc.getCondVisibility('System.Platform.ATV2')