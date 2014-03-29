# -*- coding: utf-8 -*-
import xbmc, time, os, threading, Queue, subprocess, wave
from lib import util

class PlayerHandler:
	def setSpeed(self,speed): pass
	def player(self): return None
	def getOutFile(self): raise Exception('Not Implemented')
	def play(self): raise Exception('Not Implemented')
	def isPlaying(self): raise Exception('Not Implemented')
	def stop(self): raise Exception('Not Implemented')
	def close(self): raise Exception('Not Implemented')

class PlaySFXHandler(PlayerHandler):
	_xbmcHasStopSFX = hasattr(xbmc,'stopSFX')
	def __init__(self):
		self.outDir = os.path.join(xbmc.translatePath(util.xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),'playsfx_wavs')
		if not os.path.exists(self.outDir): os.makedirs(self.outDir)
		self.outFileBase = os.path.join(self.outDir,'speech%s.wav')
		self.outFile = ''
		self._isPlaying = False 
		self.event = threading.Event()
		self.event.clear()
		
	@staticmethod
	def hasStopSFX():
		return PlaySFXHandler._xbmcHasStopSFX
		
	def _nextOutFile(self):
		self.outFile = self.outFileBase % time.time()
		return self.outFile
		
	def player(self): return 'playSFX'
	
	def getOutFile(self):
		return self._nextOutFile()

	def play(self):
		if not os.path.exists(self.outFile):
			util.LOG('playSFXHandler.play() - Missing wav file')
			return
		self._isPlaying = True
		xbmc.playSFX(self.outFile)
		f = wave.open(self.outFile,'r')
		frames = f.getnframes()
		rate = f.getframerate()
		f.close()
		duration = frames / float(rate)
		self.event.clear()
		self.event.wait(duration)
		self._isPlaying = False
		
	def isPlaying(self):
		return self._isPlaying
		
	def stop(self):
		if self._xbmcHasStopSFX:
			self.event.set()
			xbmc.stopSFX()
		
	def close(self):
		for f in os.listdir(self.outDir):
			if f.startswith('.'): continue
			os.remove(os.path.join(self.outDir,f))

class ExternalPlayerHandler(PlayerHandler):
	players = None
	playerCommands = None
	def __init__(self,preferred=None):
		outDir = os.path.join(xbmc.translatePath(util.xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),'playsfx_wavs')
		if not os.path.exists(outDir): os.makedirs(outDir)
		self.outFile = os.path.join(outDir,'speech.wav')
		self._wavProcess = None
		self._player = False
		self.speed = 0
		self.active = True
		self.getAvailablePlayers()
		self.setPlayer(preferred)
			
	def player(self):
		return self._player

	def playerAvailable(self):
		return bool(self.availablePlayers)
	
	def getAvailablePlayers(self):
		self.availablePlayers = []
		for p in self.players:
			try:
				subprocess.call(self.playerCommands[p]['available'])
				self.availablePlayers.append(p)
			except:
				pass
			
	def setPlayer(self,preferred=None):
		old = self._player
		if preferred and preferred in self.availablePlayers:
			self._player = preferred
		elif self.availablePlayers:
			self._player = self.availablePlayers[0]
		else:
			self._player = None
			
		if old != self._player: util.LOG('External Player: %s' % self._player)
		return self._player
	
	def _deleteOutFile(self):
		if os.path.exists(self.outFile): os.remove(self.outFile)
		
	def getOutFile(self):
		self._deleteOutFile()
		return self.outFile
		
	def setSpeed(self,speed):
		self.speed = speed
		
	def play(self):
		args = []
		args.extend(self.playerCommands[self._player]['play'])
		args[args.index(None)] = self.outFile
		if self.speed:
			sargs = self.playerCommands[self._player]['speed']
			if sargs:
				args.extend(sargs)
				args[args.index(None)] = str(self.speed)
		self._wavProcess = subprocess.Popen(args)
		
		while self._wavProcess.poll() == None and self.active: xbmc.sleep(10)
		
	def isPlaying(self):
		return self._wavProcess and self._wavProcess.poll() == None

	def stop(self):
		if not self._wavProcess: return
		try:
			if self.playerCommands[self._player].get('kill'):
				self._wavProcess.kill()
			else:
				self._wavProcess.terminate()
		except:
			pass
		
	def close(self):
		self.active = False
		if not self._wavProcess: return
		try:
			self._wavProcess.kill()
		except:
			pass

class UnixExternalPlayerHandler(ExternalPlayerHandler):
	players = ('aplay','sox') #By priority (aplay seems more responsive than sox)
	playerCommands = {		'aplay':{'available':('aplay','--version'), 	'play':('aplay',None), 		'speed':None},
							'sox':{'available':('sox','--version'),			'play':('play','-q',None),	'speed':('tempo','-s',None),		'kill':True}
	}
	
class WavPlayer:
	def __init__(self,external_handler=None,preferred=None):
		self.handler = None
		self.externalHandler = external_handler
		self.setPlayer(preferred)
		
	def initPlayer(self):
		if not self.usePlaySFX():
			util.LOG('stopSFX not available')
			self.useExternalPlayer()

	def usePlaySFX(self):
		if PlaySFXHandler.hasStopSFX():
			util.LOG('stopSFX available - Using xbmcPlay()')
			self.handler = PlaySFXHandler()
			return True
		return False

	def useExternalPlayer(self):
		external = None
		if self.externalHandler: external = self.externalHandler()
		if external and external.playerAvailable():
			self.handler = external
			util.LOG('Using external player')
		else:
			self.handler = PlaySFXHandler()
			util.LOG('No external player - falling back to playSFX()')
		
	def setPlayer(self,preferred=None):
		if self.handler and preferred == self.handler.player(): return 
		if preferred and self.externalHandler:
			external = self.externalHandler(preferred)
			if external.player() == preferred:
				self.handler = external
				return
		self.initPlayer()
	
	def setSpeed(self,speed):
		return self.handler.setSpeed(speed)
		
	def getOutFile(self):
		return self.handler.getOutFile()
			
	def play(self):
		return self.handler.play()
		
	def isPlaying(self):
		return self.handler.isPlaying()

	def stop(self):
		return self.handler.stop()
		
	def close(self):
		return self.handler.close()

class TTSBackendBase:
	"""The base class for all speech engine backends
		
	Subclasses must at least implement the say() method, and can use whatever
	means are available to speak text.
	"""
	provider = 'auto'
	displayName = 'Auto'
	pauseInsert = u'...'
	extras = None
	interval = 400
	broken = False
	
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

	@classmethod
	def _available(cls):
		if cls.broken and util.getSetting('disable_broken_backends',True): return False
		return cls.available()
		
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
		self.active = True
		self._threadedIsSpeaking = False
		self.queue = Queue.Queue()
		self.thread = threading.Thread(target=self._handleQueue,name='TTSThread: %s' % self.provider)
		self.thread.start()
		
	def _handleQueue(self):
		util.LOG('Threaded TTS Started: {0}'.format(self.provider))
		while self.active and not xbmc.abortRequested:
			try:
				text = self.queue.get(timeout=0.5)
				self.queue.task_done()
				if isinstance(text,int):
					time.sleep(text/1000.0)
				else:
					self._threadedIsSpeaking = True
					self.threadedSay(text)
					self._threadedIsSpeaking = False
			except Queue.Empty:
				pass
		util.LOG('Threaded TTS Finished: {0}'.format(self.provider))
			
	def _emptyQueue(self):
		try:
			while True:
				self.queue.get_nowait()
				self.queue.task_done()
		except Queue.Empty:
			return
			
	def say(self,text,interrupt=False):
		if not self.active: return
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
		self._emptyQueue()
			
class SimpleTTSBackendBase(ThreadedTTSBackend):
	WAVOUT = 0
	ENGINESPEAK = 1
	"""Handles speech engines that output wav files

	Subclasses must at least implement the runCommand() method which should
	save a wav file to outFile and/or the runCommandAndSpeak() method which
	must play the speech directly.
	"""
	def __init__(self,player=None,mode=WAVOUT):
		self.setMode(mode)
		self.player = player or WavPlayer()
		self.threadedInit()

	def setMode(self,mode):
		assert isinstance(mode,int), 'Bad mode'
		self.mode = mode
		if mode == self.WAVOUT:
			util.LOG('Mode: WAVOUT')
		else:
			util.LOG('Mode: ENGINESPEAK')

	def setPlayer(self,preferred):
		self.player.setPlayer(preferred)
	 
	def setSpeed(self,speed):
		self.player.setSpeed(speed)
		
	def runCommand(text,outFile):
		"""Convert text to speech and output to a .wav file
		
		If using WAVOUT mode, subclasses must override this method
		and output a .wav file to outFile.
		"""
		raise Exception('Not Implemented')
		
	def runCommandAndSpeak(self,text):
		"""Convert text to speech and output to a .wav file
		
		If using ENGINESPEAK mode, subclasses must override this method
		and speak text.
		"""
		raise Exception('Not Implemented')
	
	def threadedSay(self,text):
		if not text: return
		if self.mode == self.WAVOUT:
			outFile = self.player.getOutFile()
			self.runCommand(text,outFile)
			self.player.play()
		else:
			self.runCommandAndSpeak(text)

	def isSpeaking(self):
		return self.player.isPlaying() or ThreadedTTSBackend.isSpeaking(self)
		
	def _stop(self):
		self.player.stop()
		ThreadedTTSBackend._stop(self)
		
	def _close(self):
		ThreadedTTSBackend._close(self)
		self.player.close()

class LogOnlyTTSBackend(TTSBackendBase):
	provider = 'log'
	displayName = 'Log'
	def say(self,text,interrupt=False):
		util.LOG('say(Interrupt={1}): {0}'.format(repr(text),interrupt))
		
	@staticmethod
	def available():
		return True
