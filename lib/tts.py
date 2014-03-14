# -*- coding: utf-8 -*-
import os, sys, time, xbmc, subprocess
import util
import ctypes
import ctypes.util
try:
	from ctypes import windll
except ImportError:
	windll =None

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
		
class FestivalTTSBackend(TTSBackendBase):
	provider = 'festival'
	def __init__(self):
		self.startFestivalProcess()
		
	def voices(self):
		p = subprocess.Popen(['festival','-i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		d = p.communicate('(voice.list)')
		l = map(str.strip,d[0].rsplit('> (',1)[-1].rsplit(')',1)[0].split('\n'))
		return l
		
	def startFestivalProcess(self):
		#LOG('Starting Festival...')
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		pass
		
	def say(self,text,interrupt=False):
		if not text: return
		##self.festivalProcess.send_signal(signal.SIGINT)
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		voice = self.currentVoice()
		if voice: voice = '(voice_{0})\n'.format(voice)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess.communicate('{0}(SayText "{1}")\n'.format(voice,text))
		#if self.festivalProcess.poll() != None: self.startFestivalProcess()
		
	def close(self):
		#if self.festivalProcess.poll() != None: return
		#self.festivalProcess.terminate()
		pass
	
	@staticmethod
	def available():
		try:
			subprocess.call(['festival', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True

class Pico2WaveTTSBackend(TTSBackendBase):
	provider = 'pico2wav'
	def __init__(self):
		import xbmcaddon
		import os
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
		
class SAPITTSBackend(TTSBackendBase):
	provider = 'SAPI'
	interval = 100
	def __init__(self):
		import comtypes.client
		self.voice = comtypes.client.CreateObject("SAPI.SpVoice")
		
	def say(self,text,interrupt=False):
		if interrupt:
			self.voice.Speak(text.decode('utf8'),3)
		else:
			self.voice.Speak(text.decode('utf8'),1)
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')
		
class ESpeakTTSBackend(TTSBackendBase):
	provider = 'eSpeak'
	interval = 100
	def __init__(self):
		libname = ctypes.util.find_library('espeak')
		self.eSpeak = ctypes.cdll.LoadLibrary(libname)
		self.eSpeak.espeak_Initialize(0,0,None,0)
		
	def say(self,text,interrupt=False):
		if interrupt: self.eSpeak.espeak_Cancel()
		sb_text = ctypes.create_string_buffer(text)
		size = ctypes.sizeof(sb_text)
		self.eSpeak.espeak_Synth(text,size,0,0,0,0x1000,None,None)
	
	def close(self):
		self.eSpeak.espeak_Cancel()
		self.eSpeak.espeak_Terminate()
		
	@staticmethod
	def available():
		return bool(ctypes.util.find_library('espeak'))
		
class NVDATTSBackend(TTSBackendBase):
	provider = 'nvda'

	@staticmethod
	def available():
		if not windll:
			return False
		try:
			dll = windll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'nvdaControllerClient32.dll'))
			res =dll.nvdaController_testIfRunning() == 0
			del dll
			return res
		except:
			return False

	def __init__(self):
		try:
			self.dll = windll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'nvdaControllerClient32.dll'))
		except:
			self.dll =None

	def say(self,text,interrupt=False):
		if not self.dll:
			return
		if interrupt:
			self.dll.nvdaController_cancelSpeech()
		self.dll.nvdaController_speakText(text.decode("utf8"))

backends = [TTSBackendBase,SAPITTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,FliteTTSBackend,ESpeakTTSBackend,OSXSayTTSBackend,NVDATTSBackend,LogOnlyTTSBackend]
backendsByPriority = [NVDATTSBackend,SAPITTSBackend,FliteTTSBackend,ESpeakTTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,OSXSayTTSBackend,LogOnlyTTSBackend]

def selectVoice():
	import xbmcgui
	b = getBackend()()
	voices = b.voices()
	if not voices:
		xbmcgui.Dialog().ok('Not Available','No voices to select.')
		return
	idx = xbmcgui.Dialog().select('Choose Voice',voices)
	if idx < 0: return
	voice = voices[idx]
	util.LOG('Voice for {0} set to: {1}'.format(b.provider,voice))
	util.setSetting('voice.{0}'.format(b.provider),voice)
	util.setSetting('voice',voice)
		
def getBackend():
	userBackendIndex = util.getSetting('default_tts',0)
	b = backends[userBackendIndex]
	if not b.available():
 		for b in backendsByPriority:
			if b.available(): break
	return b
			
def getBackendByName(name):
	for b in backends:
		if b.provider == name and b.available():
			util.LOG('Backend: %s' % b.provider)
			return b
	return None