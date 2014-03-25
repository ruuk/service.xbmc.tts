# -*- coding: utf-8 -*-
import os, subprocess, xbmc
from lib import util
from base import WavFileTTSBackendBase

class Pico2WaveTTSBackend(WavFileTTSBackendBase):
	provider = 'pico2wave'
	displayName = 'pico2wave'
	
	extras = (('use_sox',False),)
	
	def __init__(self):
		self.process = None
		self.active = True
		self.language = self.userVoice()
		self.speed = self.userSpeed()
		self.useSOX = False
		self.checkForSox()
		self.updateSoxUsage()
		WavFileTTSBackendBase.__init__(self)
		
	def checkForSox(self):
		try:
			subprocess.call(['sox','--version'])
			self._soxAvailable = True
		except:
			self._soxAvailable = False

	def updateSoxUsage(self):
		useSOX = self.useSOX
		self.useSOX = self.userExtra('use_sox',False) and self._soxAvailable
		if not useSOX and self.useSOX: util.LOG('Using SOX')
		
	def runCommand(self,text):
		args = ['pico2wave']
		if self.language: args += ['-l',self.language]
		args += ['-w', '{0}'.format(self.outFile), '{0}'.format(text)]
		subprocess.call(args)
		
	def play(self):
		if self.useSOX:
			args = ['play','-q',self.outFile]
			if self.speed: args += ['tempo','-s',str(self.speed/100.0)]
			self.process = subprocess.Popen(args)
		else:
			self.process = subprocess.Popen(['aplay',self.outFile])
		while self.process.poll() == None and self.active: xbmc.sleep(10)
		
	def isSpeaking(self):
		return (self.process and self.process.poll() == None) or WavFileTTSBackendBase.isSpeaking(self)
		
	def voices(self):
		try:
			out = subprocess.check_output(['pico2wave','-l','NONE','-w','/dev/null','X'],stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError, e:
			out = e.output
		if not 'languages:' in out: return None
		
		return out.split('languages:',1)[-1].split('\n\n')[0].strip('\n').split('\n')
		
	def update(self,voice_name,speed):
		if voice_name: self.language = voice_name
		if speed: self.speed = speed
		self.updateSoxUsage()
		
	def stop(self):
		if not self.process: return
		try:
			if self.useSOX:
				self.process.kill()
			else:
				self.process.terminate()
		except:
			pass
		
	def close(self):
		self.active = False
		try:
			self.process.kill()
		except:
			pass
		
	@staticmethod
	def available():
		try:
			subprocess.call(['pico2wave', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True