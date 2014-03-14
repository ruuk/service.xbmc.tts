# -*- coding: utf-8 -*-
from lib import util
from base import TTSBackendBase, LogOnlyTTSBackend
from nvda import NVDATTSBackend
from festival import FestivalTTSBackend
from pico2wave import Pico2WaveTTSBackend
from flite import FliteTTSBackend
from osxsay import OSXSayTTSBackend
from sapi import SAPITTSBackend
from espeak import ESpeakTTSBackend


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