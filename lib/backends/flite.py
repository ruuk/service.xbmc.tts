# -*- coding: utf-8 -*-
import os, subprocess, time, threading, wave, xbmc
from lib import util
from base import ThreadedTTSBackend

class FliteTTSBackend(ThreadedTTSBackend):
	provider = 'Flite'
	interval = 100
	
	def __init__(self):
		self.process = None
		self.threadedInit()
		
	def threadedSay(self,text):
		if not text: return
		voice = self.currentVoice() or 'kal16'
		self.process = subprocess.Popen(['flite', '-voice', voice, '-t', text])
		self.process.wait()
		
	def threadedInterrupt(self):
		self.stopProcess()
		
	def stopProcess(self):
		if self.process:
			try:
				self.process.terminate()
				self.process.wait()
			except:
				pass
			
	def voices(self):
		return subprocess.check_output(['flite','-lv']).split(': ',1)[-1].strip().split(' ')
		
	def stop(self):
		self.process.terminate()
		
	def close(self):
		self.stopProcess()
		self.threadedClose()

	@staticmethod
	def available():
		try:
			subprocess.call(['flite', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True

class FliteATV2TTSBackend(ThreadedTTSBackend):
	provider = 'FliteATV2'
	interval = 50

	def __init__(self):
		self.outDir = os.path.join(xbmc.translatePath(util.xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'),'fliteatv2wavs')
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
		util.LOG('FliteATV2 wav output: ' + self.outDir)
		
	def deleteOutfile(self):
		if os.path.exists(self.outFile): os.remove(self.outFile)
		
	def nextOutFile(self):
		self.outFile = self.outFileBase % time.time()
		
	def threadedSay(self,text):
		if not text: return
		self.deleteOutfile()
		self.nextOutFile()
		os.system('flite -t "{0}" -o "{1}"'.format(text,self.outFile))
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
			
	@staticmethod
	def available():
		if not xbmc.getCondVisibility('System.Platform.ATV2'): return False
		try:
			return not os.system('flite --help')
		except (OSError, IOError):
			raise
		return True

#class FliteTTSBackend(TTSBackendBase):
#	provider = 'Flite'
#	def __init__(self):
#		import ctypes
#		self.flite = ctypes.CDLL('libflite.so.1',mode=ctypes.RTLD_GLOBAL)
#		flite_usenglish = ctypes.CDLL('libflite_usenglish.so.1',mode=ctypes.RTLD_GLOBAL) #analysis:ignore
#		flite_cmulex = ctypes.CDLL('libflite_cmulex.so.1',mode=ctypes.RTLD_GLOBAL) #analysis:ignore
#		flite_cmu_us_slt = ctypes.CDLL('libflite_cmu_us_slt.so.1')
#		self.flite.flite_init()
#		self.voice = flite_cmu_us_slt.register_cmu_us_slt()
#
#	def say(self,text,interrupt=False):
#		if not text: return
#		self.flite.flite_text_to_speech(text,self.voice,'play')
#		
#		
#	@staticmethod
#	def available():
#		try:
#			import ctypes
#			ctypes.CDLL('libflite.so.1')
#		except (OSError, IOError):
#			return False
#		return True
		
#class FliteTTSBackend(TTSBackendBase):
#	provider = 'Flite'
#
#	def say(self,text,interrupt=False):
#		if not text: return
#		voice = self.currentVoice() or 'kal16'
#		subprocess.call(['flite', '-voice', voice, '-t', text])
#		
#	def voices(self):
#		return subprocess.check_output(['flite','-lv']).split(': ',1)[-1].strip().split(' ')
#		
#	@staticmethod
#	def available():
#		try:
#			subprocess.call(['flite', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
#		except (OSError, IOError):
#			return False
#		return True