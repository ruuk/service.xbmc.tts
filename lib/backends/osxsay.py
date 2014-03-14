# -*- coding: utf-8 -*-
import sys, subprocess
from base import ThreadedTTSBackend

class OSXSayTTSBackend(ThreadedTTSBackend):
	provider = 'OSXSay'
	interval = 100
	
	def __init__(self):
		self.process = None
		self.threadedInit()
		
	def threadedSay(self,text):
		if not text: return
		self.process = subprocess.Popen(['say', text])
		self.process.wait()
		
	def threadedInterrupt(self):
		self.stopProcess()
		
	def stopProcess(self):
		if self.process:
			try:
				self.process.terminate()
			except:
				pass
		
	def close(self):
		self.stopProcess()
		self.threadedClose()

	@staticmethod
	def available():
		return sys.platform == 'darwin'