# -*- coding: utf-8 -*-
import os, time, sys, xbmc, subprocess
import util

class TTSBackendBase:
	provider = None
	def say(self,text): raise Exception('Not Implemented')

	def close(self): pass

	def pause(self,ms=500): xbmc.sleep(ms)
	@staticmethod
	def available(): return False
	
class LogOnlyTTSBackend(TTSBackendBase):
	provider = 'log'
	def say(self,text):
		print 'TTS: ' + repr(text)
		
	@staticmethod
	def available():
		return True
		
class FestivalTTSBackend(TTSBackendBase):
	provider = 'festival'
	def __init__(self):
		self.startFesticalProcess()
		
	def startFesticalProcess(self):
		#LOG('Starting Festival...')
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		pass
		
	def say(self,text):
		if not text: return
		##self.festivalProcess.send_signal(signal.SIGINT)
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess.communicate('(SayText "{0}")\n'.format(text))
		#if self.festivalProcess.poll() != None: self.startFesticalProcess()
		
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
		
	def say(self,text):
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
		
class FLiteTTSBackend(TTSBackendBase):
	provider = 'flite'
	def __init__(self):
		import xbmcaddon
		import os
		profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
		if not os.path.exists(profile): os.makedirs(profile)
		self.outFileBase = profile
		self.wave = None
		self.useFileMethod = False
		if util.isATV2():
			self.useFileMethod = True
			try:
				import wave
				self.wave = wave
			except:
				self.useFileMethod = False
		
	def getWavDuration(self,path):
		if not self.wave: return 0
		w = self.wave.open(path,'r')
		frames = w.getnframes()
		rate = w.getframerate()
		w.close()
		return int((frames / float(rate)) * 1000)
			
	def say(self,text):
		if not text: return
		#flite -voice slt -t "this is a test"
		if self.useFileMethod:
			outFile = os.path.join(self.outFileBase,str(time.time()) + '.wav')
			subprocess.call(['flite', '-t', '{0}'.format(text), '{0}'.format(outFile)])
			xbmc.playSFX(outFile)
			xbmc.sleep(self.getWavDuration(outFile))
			os.remove(outFile)
		else:
			subprocess.call(['flite', '-t', '{0}'.format(text)])
			
	def close(self):
		if not self.useFileMethod: return
		#make sure we didn't leave any wavs behind
		for f in os.listdir(self.outFileBase):
			if f.endswith('.wav'): os.remove(os.path.join(self.outFileBase,f))
		
	@staticmethod
	def available():
		try:
			subprocess.call(['flite', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
			if util.isATV2(): import wave #analysis:ignore
		except (OSError, IOError):
			return False
		return True
		
class WindowsInternalTTSBackend(TTSBackendBase):
	provider = 'windowstts'
	def __init__(self):
		import xbmcaddon
		import os
		profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
		if not os.path.exists(profile): os.makedirs(profile)
		self.vbsFile = os.path.join(profile,'witts.vbs')
		util.LOG('Windows Internal VBS file: ' + self.vbsFile)
		self.vbs =		'set speech = Wscript.CreateObject("SAPI.spVoice")\n'
		self.vbs +=	'speech.speak "{0}"\n'
		#-- Look into using this directly
		#import win32com.client
		#voice = win32com.client.Dispatch("SAPI.SpVoice")
		#voice.Speak(phrase)
		
	def say(self,text):
		if not text: return
		with open(self.vbsFile,'w') as f: f.write(self.vbs.format(text))
		subprocess.call(['Wscript.exe',self.vbsFile])
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')
		
backends = [WindowsInternalTTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,FLiteTTSBackend,LogOnlyTTSBackend]

def getBackend():
	userBackendIndex = util.getSetting('default_tts',0)
	b = backends[userBackendIndex]
	if b.available(): return b()
	
	for b in backends:
		if b.available():
			util.LOG('TTS: %s' % b.provider)
			return b