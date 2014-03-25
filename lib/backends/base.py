# -*- coding: utf-8 -*-
import xbmc, time, os, threading, wave
from lib import util

class TTSBackendBase:
	"""The base class for all speech engine backends
		
	Subclasses must at least implement the say() method, and can use whatever
	means are available to speak text.
	"""
	provider = 'auto'
	displayName = 'Auto'
	pauseInsert = '...'
	extras = None
	
	interval = 400
	def say(self,text,interrupt=False):
		"""Method accepting text to be spoken
		
		Must be overridden by subclasses.
		text is unicode and the text to be spoken.
		If interrupt is True, the subclass should interrupt all previous speech.
		
		"""
		raise Exception('Not Implemented')

	def sayList(self,texts,interrupt=False):
		"""Accepts a list of text strings to be spoken
		
		May be overriden by subclasses. The default implementation calls say()
		for each item in texts, calling insertPause() between each.
		If interrupt is True, the subclass should interrupt all previous speech.
		"""
		self.say(texts.pop(0),interrupt=interrupt)
		for t in texts:
			self.insertPause()
			self.say(t)
		
	def voices(self):
		"""Returns a list of voice string names
		
		May be overridden by subclasses. Default implementation returns None.
		"""
		return None
	
	def userVoice(self):
		"""Returns a user saved voice name
		"""
		self._voice = util.getSetting('voice.{0}'.format(self.provider),'')
		return self._voice
		
	def userSpeed(self):
		"""Returns a user saved speed integer
		"""
		self._speed = util.getSetting('speed.{0}'.format(self.provider),0)
		return self._speed

	def userExtra(self,extra,default=None):
		"""Returns a user saved extra setting named key, or default if not set
		"""
		setattr(self,extra,util.getSetting('{0}.{1}'.format(extra,self.provider),default))
		return getattr(self,extra)
		
	def insertPause(self,ms=500):
		"""Insert a pause of ms milliseconds
		
		May be overridden by sublcasses. Default implementation sleeps for ms.
		"""
		xbmc.sleep(ms)
	
	def isSpeaking(self):
		"""Returns True if speech engine is currently speaking, False if not 
		and None if unknown
		
		Subclasses should override this respond accordingly
		"""
		return None
		
	def update(self,voice_name,speed):
		"""Called when the user has changed voice or speed
		
		Voice will be the new voice name or None if not changed.
		Speed will be the speed integer on None if not changed.
		Subclasses should override this to react to user changes.
		"""
		pass
	
	def stop(self):
		"""Stop all speech, implicitly called when close() is called
		
		Subclasses shoud override this to respond to requests to stop speech.
		Default implementation does nothing.
		"""
		pass
	
	def close(self):
		"""Close the speech engine
		
		Subclasses shoud override this to clean up after themselves.
		Default implementation does nothing.
		"""
		pass
	
	def _update(self):
		voice = self._updateVoice()
		speed = self._updateSpeed()
		extras = self._updateExtras()
		if voice or speed or extras: self.update(voice,speed)
		
	def _updateVoice(self):
		old = hasattr(self,'_voice') and self._voice or None
		voice = self.userVoice()
		if old != None:
			if voice == old: return None
		else:
			return None
		return voice
		
	def _updateSpeed(self):
		old = hasattr(self,'_speed') and self._speed or None
		speed = self.userSpeed()
		if old != None:
			if speed == old: return None
		else:
			return None
		return speed
			
	def _updateExtras(self):
		if not self.extras: return False
		for (extra,default) in self.extras:
			old = None
			if hasattr(self, extra): old = getattr(self,extra)
			new = self.userExtra(extra,default)
			if old != None and new != old: return True
		return False
		
	def _stop(self):
		self.stop()
	
	def _close(self):
		self._stop()
		self.close()

	@staticmethod
	def available():
		"""Static method representing the the speech engines availability
		
		Subclasses should override this and return True if the speech engine is
		capable of speaking text in the current environment.
		Default implementation returns False.
		"""
		return False

class ThreadedTTSBackend(TTSBackendBase):
	"""A threaded speech engine backend
		
	Handles all the threading mechanics internally.
	Subclasses must at least implement the threadedSay() method, and can use
	whatever means are available to speak text.
	They say() and sayList() and insertPause() methods are not meant to be overridden.
	"""
	
	def __init__(self):
		self.threadedInit()
		
	def threadedInit(self):
		"""Initialize threading
		
		Must be called if you override the __init__() method
		"""
		import Queue
		self.active = True
		self._threadedIsSpeaking = False
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
				self._threadedIsSpeaking = True
				self.threadedSay(text)
				self._threadedIsSpeaking = False
		util.LOG('Threaded TTS Finished: {0}'.format(self.provider))
			
	def _emptyQueue(self):
		try:
			while True:
				self.queue.get_nowait()
				self.queue.task_done()
		except:
			return
			
	def say(self,text,interrupt=False):
		if interrupt: self._stop()
		self.queue.put_nowait(text)
		
	def sayList(self,texts,interrupt=False):
		if interrupt: self._stop()
		self.queue.put_nowait(texts.pop(0))
		for t in texts: 
			self.insertPause()
			self.queue.put_nowait(t)
		
	def isSpeaking(self):
		return self._threadedIsSpeaking or not self.queue.empty()
		
	def _stop(self):
		self._emptyQueue()
		TTSBackendBase._stop(self)

	def insertPause(self,ms=500):
		self.queue.put(ms)
	
	def threadedSay(self,text):
		"""Method accepting text to be spoken
		
		Subclasses must override this method and should speak the unicode text.
		Speech interruption is implemented in the stop() method.
		"""
		raise Exception('Not Implemented')
		
	def _close(self):
		self.active = False
		TTSBackendBase._close(self)

class WavFileTTSBackendBase(ThreadedTTSBackend):
	"""Handles speech engines that output wav files
	
	Uses XBMC audio via xbmc.playSFX() if xbmc.stopSFX() is available or play()
	is not implemented.
	Subclasses must at least implement the runCommand() method which should
	save a wav file to the path in the instance's outFile attribute.
	Subclasses should also implement a play() method if possible to handle the
	situation where xbmc.stopSFX is not available otherwise speech will not be
	interruptible. xbmc.stopSFX() is not available in Frodo, and is only
	available as a patch as of 03-21-2014.
	"""
	def __init__(self):
		self.outDir = os.path.join(xbmc.translatePath(util.xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),'playsfx_wavs')
		if not os.path.exists(self.outDir): os.makedirs(self.outDir)
		self.outFileBase = os.path.join(self.outDir,'speech%s.wav')
		self.outFile = ''
		self._WFTTSisSpeaking = False 
		self.event = threading.Event()
		self.event.clear()
		self._xbmcHasStopSFX = False
		if hasattr(xbmc,'stopSFX'):
			util.LOG('stopSFX available')
			self._play = self.xbmcPlay
			self._xbmcHasStopSFX = True
		else:
			util.LOG('stopSFX not available')
			if self.play:
				self._play = self.play
			else:
				self._play = self.xbmcPlay
		
		self.threadedInit()
		util.LOG('{0} wav output: {1}'.format(self.provider,self.outDir))
		
	def runCommand(text):
		"""Convert text to speech and output to a .wav file
		
		Subclasses must override this method, and output a .wav file to the
		path in the outFile attribute.
		"""
		raise Exception('Not Implemented')

	def _deleteOutfile(self):
		if os.path.exists(self.outFile): os.remove(self.outFile)
		
	def _nextOutFile(self):
		self.outFile = self.outFileBase % time.time()
		
	def _play(self): pass

	play = None

	def xbmcPlay(self):
		if not os.path.exists(self.outFile):
			util.LOG('xbmcPlay() - Missing wav file')
			return
		self._WFTTSisSpeaking = True
		xbmc.playSFX(self.outFile)
		f = wave.open(self.outFile,'r')
		frames = f.getnframes()
		rate = f.getframerate()
		f.close()
		duration = frames / float(rate)
		self.event.clear()
		self.event.wait(duration)
		self._WFTTSisSpeaking = False
		
	def threadedSay(self,text):
		if not text: return
		self._deleteOutfile()
		self._nextOutFile()
		self.runCommand(text)
		self._play()
		
	def isSpeaking(self):
		return self._WFTTSisSpeaking or ThreadedTTSBackend.isSpeaking(self)
		
	def _stop(self):
		if self._xbmcHasStopSFX:
			self.event.set()
			xbmc.stopSFX()
		ThreadedTTSBackend._stop(self)
		
	def _close(self):
		ThreadedTTSBackend._close(self)
		for f in os.listdir(self.outDir):
			if f.startswith('.'): continue
			os.remove(os.path.join(self.outDir,f))

class LogOnlyTTSBackend(TTSBackendBase):
	provider = 'log'
	displayName = 'Log'
	def say(self,text,interrupt=False):
		util.LOG('say(Interrupt={1}): {0}'.format(repr(text),interrupt))
		
	@staticmethod
	def available():
		return True
