# -*- coding: utf-8 -*-
import sys, xbmc, time, xbmcaddon

DEBUG = True

def info(key):
	return xbmcaddon.Addon().getAddonInfo(key)
	
def ERROR(txt,hide_tb=False):
	if isinstance (txt,str): txt = txt.decode("utf-8")
	short = str(sys.exc_info()[1])
	if hide_tb:
		LOG('ERROR: {0} - {1}'.format(txt,short))
		return short
	LOG('ERROR: ' + txt)
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

def installKeymap():
	import os, xbmcvfs, xbmcgui
	targetPath = os.path.join(xbmc.translatePath('special://userdata').decode('utf-8'),'keymaps','service.xbmc.tts.keyboard.xml')
	sourcePath = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8'),'resources','service.xbmc.tts.keyboard.xml')
	if os.path.exists(targetPath): xbmcvfs.delete(targetPath)
	success = xbmcvfs.copy(sourcePath,targetPath)
	if success:
		xbmcgui.Dialog().ok('Installed','Keymap installed successfully!','','Restart XBMC to use.')
	else:
		xbmcgui.Dialog().ok('Failed','Keymap installation failure.')
	
def selectBackend():
	import backends
	import xbmcgui
	choices = ['auto']
	display = ['Auto']
	for b in backends.backendsByPriority:
		if b.available():
			choices.append(b.provider)
			display.append(b.displayName)
	idx = xbmcgui.Dialog().select('Choose Backend',display)
	if idx < 0: return
	setSetting('backend',choices[idx])
	
LAST_COMMAND_DATA = ''

def initCommands():
	global LAST_COMMAND_DATA
	LAST_COMMAND_DATA = ''
	setSetting('EXTERNAL_COMMAND','')

def sendCommand(command):
	commandData = '{0}:{1}'.format(time.time(),command)
	setSetting('EXTERNAL_COMMAND',commandData)
	
def getCommand():
	global LAST_COMMAND_DATA
	commandData = getSetting('EXTERNAL_COMMAND','')
	if commandData == LAST_COMMAND_DATA: return None
	LAST_COMMAND_DATA = commandData
	return commandData.split(':',1)[-1]
	