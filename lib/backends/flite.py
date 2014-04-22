# -*- coding: utf-8 -*-
import os, subprocess
from lib import util
import base
import audio

class FliteTTSBackend(base.SimpleTTSBackendBase):
	provider = 'Flite'
	displayName = 'Flite'
	settings = {	'voice':'kal16',
					'output_via_flite':False
	}
	interval = 100
	
	def __init__(self):
		self.onATV2 = util.isATV2()
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler)
		base.SimpleTTSBackendBase.__init__(self,player, self.getMode())
		self.process = None
		self.voice = self.setting('voice')
		
	def runCommand(self,text,outFile):
		if self.onATV2:
			os.system('flite -t "{0}" -o "{1}"'.format(text,outFile))
		else:
			subprocess.call(['flite', '-voice', self.voice, '-t', text,'-o',outFile])
		return True
		
	def runCommandAndSpeak(self,text):
		self.process = subprocess.Popen(['flite', '-voice', self.voice, '-t', text])
		while self.process.poll() == None and self.active: util.sleep(10)

	def voices(self):
		if self.onATV2: return None
		return subprocess.check_output(['flite','-lv']).split(': ',1)[-1].strip().split(' ')
		
	def update(self):
		self.voice = self.setting('voice')
		self.setMode(self.getMode())

	def getMode(self):
		if not self.onATV2 and self.setting('output_via_flite'):
			return base.SimpleTTSBackendBase.ENGINESPEAK
		else:
			return base.SimpleTTSBackendBase.WAVOUT
			
	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	@staticmethod
	def available():
		try:
			subprocess.call(['flite', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return util.isATV2() and util.commandIsAvailable('flite')
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