# -*- coding: utf-8 -*-
import os, sys, xbmc, subprocess
import util

class TTSBackendBase:
	provider = None
	def say(self,text): raise Exception('Not Implemented')

	def voices(self): return []
	
	def setVoice(self,voice): pass

	def currentVoice(self): return util.getSetting('voice.{0}'.format(self.provider),'')
		
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
		
	def voices(self):
		p = subprocess.Popen(['festival','-i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		d = p.communicate('(voice.list)')
		l = map(str.strip,d[0].rsplit('> (',1)[-1].rsplit(')',1)[0].split('\n'))
		return l
		
	def startFesticalProcess(self):
		#LOG('Starting Festival...')
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		pass
		
	def say(self,text):
		if not text: return
		##self.festivalProcess.send_signal(signal.SIGINT)
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		voice = self.currentVoice()
		if voice: voice = '(voice_{0})\n'.format(voice)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess.communicate('{0}(SayText "{1}")\n'.format(voice,text))
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
	def say(self,text):
		if not text: return
		voice = self.currentVoice() or 'kal16'
		subprocess.call(['flite', '-voice', voice, '-t', text])
		
	def voices(self):
		return subprocess.check_output(['flite','-lv']).split(': ',1)[-1].strip().split(' ')
		
	@staticmethod
	def available():
		try:
			subprocess.call(['flite', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
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
	
def settingsBackend():
	userBackendIndex = util.getSetting('default_tts',-1)
	if userBackendIndex < 0: return None
	return backends[userBackendIndex]
		
def getBackend():
	userBackendIndex = util.getSetting('default_tts',0)
	b = backends[userBackendIndex]
	if b.available():
		util.LOG('TTS: %s' % b.provider)
		return b
	
	for b in backends:
		if b.available():
			util.LOG('TTS: %s' % b.provider)
			return b
			
def getBackendByName(name):
	for b in backends:
		if b.provider == name and b.available():
			util.LOG('TTS: %s' % b.provider)
			return b
	return None