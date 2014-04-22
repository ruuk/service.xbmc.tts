# -*- coding: utf-8 -*-
from lib import util
from base import LogOnlyTTSBackend
from nvda import NVDATTSBackend
from festival import FestivalTTSBackend
from pico2wave import Pico2WaveTTSBackend
from flite import FliteTTSBackend
from osxsay import OSXSayTTSBackend
from sapi import SAPITTSBackend
from espeak import ESpeakTTSBackend, ESpeakCtypesTTSBackend
from speechdispatcher import SpeechDispatcherTTSBackend
from jaws import JAWSTTSBackend
from sjhttsd import SJHttsdTTSBackend

backendsByPriority = [JAWSTTSBackend,NVDATTSBackend,SAPITTSBackend,SpeechDispatcherTTSBackend,FliteTTSBackend,ESpeakTTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,OSXSayTTSBackend,SJHttsdTTSBackend,ESpeakCtypesTTSBackend,LogOnlyTTSBackend]

def getBackendFallback():
	if util.isATV2():
		return FliteTTSBackend 
	elif util.isWindows():
		return SAPITTSBackend
	elif util.isOSX():
		return OSXSayTTSBackend
	elif util.isOpenElec():
		return ESpeakTTSBackend
	for b in backendsByPriority:
		if b._available(): return b
	return None
	
def getVoices(provider):
	voices = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		voices = b.voices()
	return voices
		
def selectVoice(provider):
	import xbmcgui
	voices = getVoices(provider)
	if not voices:
		xbmcgui.Dialog().ok('Not Available','No voices to select.')
		return
	idx = xbmcgui.Dialog().select('Choose Voice',voices)
	if idx < 0: return
	voice = voices[idx]
	util.LOG('Voice for {0} set to: {1}'.format(provider,voice))
	util.setSetting('voice.{0}'.format(provider),voice)
	
def getLanguages(provider):
	languages = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		languages = b.languages()
	return languages

def selectLanguage(provider):
	import xbmcgui
	languages = getLanguages(provider)
	if not languages:
		xbmcgui.Dialog().ok('Not Available','No languages to select.')
		return
	idx = xbmcgui.Dialog().select('Choose Language',languages)
	if idx < 0: return
	language = languages[idx]
	util.LOG('Language for {0} set to: {1}'.format(provider,language))
	util.setSetting('language.{0}'.format(provider),language)
	
def selectPlayer(provider):
	import xbmcgui
	players = None
	bClass = getBackendByProvider(provider)
	if bClass and hasattr(bClass,'players'):
		b = bClass()
		players = b.players()
	if not players:
		xbmcgui.Dialog().ok('Not Available','No players to select.')
		return
	players.insert(0,('','Auto'))
	disp = []
	for p in players: disp.append(p[1])
	idx = xbmcgui.Dialog().select('Choose Player',disp)
	if idx < 0: return
	player = players[idx][0]
	util.LOG('Player for {0} set to: {1}'.format(b.provider,player))
	util.setSetting('player.{0}'.format(b.provider),player)
		
def getBackend(provider='auto'):
	provider = util.getSetting('backend') or provider
	b = getBackendByProvider(provider)
	if not b or not b._available():
 		for b in backendsByPriority:
			if b._available(): break
	return b

def getWavStreamBackend(provider='auto'):
	b = getBackendByProvider(provider)
	if not b or not b._available() or not b.canStreamWav:
 		for b in backendsByPriority:
			if b._available() and b.canStreamWav: break
	return b
	
def getBackendByProvider(name):
	if name == 'auto': return None
	for b in backendsByPriority:
		if b.provider == name and b._available():
			return b
	return None
