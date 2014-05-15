# -*- coding: utf-8 -*-
import xbmc, xbmcaddon

def getXBMCVersion():
	import json
	resp = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
	data = json.loads(resp)
	if not 'result' in data: return None
	if not 'version' in data['result']: return None
	return data['result']['version']

BASE = '{ "jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.xbmc.tts","enabled":%s}, "id": 1 }'

def enableAddon():
	xbmc.executeJSONRPC(BASE % 'true') #So enable it instead
	
def disableAddon():
	version = getXBMCVersion()
	if not version or version['major'] < 13: return #Disabling in this manner crashes on Frodo
	xbmc.executeJSONRPC(BASE % 'false') #Try to disable it
	#if res and 'error' in res: #If we have an error, it's already disabled
	#print res
	
def toggleEnabled():
	try:
		xbmcaddon.Addon('service.xbmc.tts')
		xbmc.executebuiltin('XBMC.RunScript(service.xbmc.tts,key.SHUTDOWN)')
	except:
		enableAddon()
		
if __name__ == '__main__':
	toggleEnabled()