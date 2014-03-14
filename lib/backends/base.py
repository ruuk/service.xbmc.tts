# -*- coding: utf-8 -*-
import xbmc, time
from lib import util

class TTSBackendBase:
	provider = None
	interval = 400
	def say(self,text,interrupt=False): raise Exception('Not Implemented')

	def voices(self): return []
	
	def setVoice(self,voice): pass

	def currentVoice(self): return util.getSetting('voice.{0}'.format(self.provider),'')
		
	def close(self): pass

	def pause(self,ms=500): xbmc.sleep(ms)
	
	@staticmethod
	def available(): return False

class ThreadedTTSBackend(TTSBackendBase):
	def threadedInit(self):
		import threading
		import Queue
		self.active = True
		self.queue = Queue.Queue()
		self.thread = threading.Thread(target=self._handleQueue,name='TTSThread')
		self.thread.start()
		
	def _handleQueue(self):
		util.LOG('Threaded TTS Started: {0}'.format(self.provider))
		while self.active:
			text = self.queue.get()
			if isinstance(text,int):
				time.sleep(text/1000.0)
			else:
				self.threadedSay(text)
		util.LOG('Threaded TTS Finished: {0}'.format(self.provider))
			
	def _emptyQueue(self):
		try:
			while True:
				self.queue.get_nowait()
				self.queue.task_done()
		except:
			return
			
	def say(self,text,interrupt=False):
		if interrupt:
			self._emptyQueue()
			self.threadedInterrupt()
		self.queue.put_nowait(text)
	
	def pause(self,ms=500):
		self.queue.put(ms)
	
	def threadedSay(self,text): raise Exception('Not Implemented')
		
	def threadedInterrupt(self): raise Exception('Not Implemented')

	def threadedClose(self):
		self.active = False
		
	def close(self):
		self.threadedClose()
		
class LogOnlyTTSBackend(TTSBackendBase):
	provider = 'log'
	def say(self,text,interrupt=False):
		util.LOG('say(Interrupt={1}): {0}'.format(repr(text),interrupt))
		
	@staticmethod
	def available():
		return True
