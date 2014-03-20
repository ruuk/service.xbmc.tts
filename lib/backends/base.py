# -*- coding: utf-8 -*-
import xbmc, time, os, threading, wave
from lib import util

class TTSBackendBase:
	provider = 'auto'
	displayName = 'Auto'
	
	interval = 400
	def say(self,text,interrupt=False): raise Exception('Not Implemented')

	def voices(self): return []
	
	def setVoice(self,voice): pass

	def currentVoice(self): return util.getSetting('voice.{0}'.format(self.provider),'')
		
	def currentSpeed(self): return util.getSetting('speed.{0}'.format(self.provider),'')
		
	def close(self): pass

	def pause(self,ms=500): xbmc.sleep(ms)
	
	def stop(self): pass

	@staticmethod
	def available(): return False

class ThreadedTTSBackend(TTSBackendBase):
	def threadedInit(self):
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
		self._emptyQueue()
		
	def close(self):
		self.threadedClose()
		
class XBMCAudioTTSBackendBase(ThreadedTTSBackend):
	def __init__(self):
		self.outDir = os.path.join(xbmc.translatePath(util.xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),'playsfx_wavs')
		if not os.path.exists(self.outDir): os.makedirs(self.outDir)
		self.outFileBase = os.path.join(self.outDir,'speech%s.wav')
		self.outFile = ''
		self.event = threading.Event()
		self.event.clear()
		self._xbmcHasStopSFX = False
		try:
			self.stopSFX = xbmc.stopSFX
			self._xbmcHasStopSFX = True
		except:
			pass
		
		self.threadedInit()
		util.LOG('{0} wav output: {1}'.format(self.provider,self.outDir))
		
	def runCommand(): raise Exception('Not Implemented')
	
	def deleteOutfile(self):
		if os.path.exists(self.outFile): os.remove(self.outFile)
		
	def nextOutFile(self):
		self.outFile = self.outFileBase % time.time()
		
	def threadedSay(self,text):
		if not text: return
		self.deleteOutfile()
		self.nextOutFile()
		self.runCommand(text)
		xbmc.playSFX(self.outFile)
		f = wave.open(self.outFile,'r')
		frames = f.getnframes()
		rate = f.getframerate()
		f.close()
		duration = frames / float(rate)
		self.event.clear()
		self.event.wait(duration)
		
	def threadedInterrupt(self):
		self.stop()
		
	def stop(self):
		if self._xbmcHasStopSFX: #If not available, then we force the event to stay cleared. Unfortunately speech will be uninterruptible
			self.event.set()
			xbmc.stopSFX()
		
	def close(self):
		self.stop()
		for f in os.listdir(self.outDir):
			if f.startswith('.'): continue
			os.remove(os.path.join(self.outDir,f))
		self.threadedClose()

class LogOnlyTTSBackend(TTSBackendBase):
	provider = 'log'
	displayName = 'Log'
	def say(self,text,interrupt=False):
		util.LOG('say(Interrupt={1}): {0}'.format(repr(text),interrupt))
		
	@staticmethod
	def available():
		return True
