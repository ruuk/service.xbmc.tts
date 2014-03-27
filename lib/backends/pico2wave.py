# -*- coding: utf-8 -*-
import os, subprocess
from base import WavFileTTSBackendBase, UnixWavPlayer

class Pico2WaveTTSBackend(UnixWavPlayer,WavFileTTSBackendBase):
	provider = 'pico2wave'
	displayName = 'pico2wave'
	
	extras = (('use_sox',False),)
	
	def __init__(self):
		UnixWavPlayer.__init__(self)
		WavFileTTSBackendBase.__init__(self)
		
		self.language = self.userVoice()
		self.wavPlayerSpeed = self.userSpeed() * 0.01
		self.setSox()
		
	def runCommand(self,text):
		args = ['pico2wave']
		if self.language: args.extend(['-l',self.language])
		args.extend(['-w', '{0}'.format(self.outFile), '{0}'.format(text)])
		subprocess.call(args)
		
	def isSpeaking(self):
		return self.isPlaying() or WavFileTTSBackendBase.isSpeaking(self)
		
	def voices(self):
		try:
			out = subprocess.check_output(['pico2wave','-l','NONE','-w','/dev/null','X'],stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError, e:
			out = e.output
		if not 'languages:' in out: return None
		
		return out.split('languages:',1)[-1].split('\n\n')[0].strip('\n').split('\n')
		
	def update(self,voice_name,speed):
		if voice_name: self.language = voice_name
		if speed: self.wavPlayerSpeed = speed * 0.01
		self.setSox()
		
	def setSox(self):
		preferred = None
		if self.userExtra('use_sox',False): preferred = 'sox'
		if self.setPlayer(preferred) == 'sox':
			self.useExternalPlayer()
		
	def canPlayExternal(self):
		return self.playerAvailable()
		
	def stop(self):
		self.stopPlaying()
		
	def close(self):
		self.closePlayer()
		
	@staticmethod
	def available():
		try:
			subprocess.call(['pico2wave', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True