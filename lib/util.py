# -*- coding: utf-8 -*-
import sys, xbmc, xbmcaddon

DEBUG = True

def info(key):
	return xbmcaddon.Addon().getAddonInfo(key)
	
def ERROR(txt):
	if isinstance (txt,str): txt = txt.decode("utf-8")
	LOG('ERROR: ' + txt)
	short = str(sys.exc_info()[1])
	import traceback
	traceback.print_exc()
	return short
	
def LOG(message):
	message = 'service.xbmc.tts: ' + message
	xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGNOTICE)
	
def getSetting(key,default=None):
	setting = xbmcaddon.Addon().getSetting(key)
	return _processSetting(setting,default)

def _processSetting(setting,default):
	if not setting: return default
	if isinstance(default,bool):
		return setting.lower() == 'true'
	elif isinstance(default,int):
		return int(float(setting or 0))
	elif isinstance(default,list):
		if setting: return setting.split(':!,!:')
		else: return default
	
	return setting

def setSetting(key,value):
	value = _processSettingForWrite(value)
	xbmcaddon.Addon().setSetting(key,value)
	
def _processSettingForWrite(value):
	if isinstance(value,list):
		value = ':!,!:'.join(value)
	elif isinstance(value,bool):
		value = value and 'true' or 'false'
	return str(value)
	
def isATV2():
	return xbmc.getCondVisibility('System.Platform.ATV2')