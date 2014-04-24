# -*- coding: utf-8 -*-
import xbmc

def getXBMCVersion():
	import json
	resp = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
	data = json.loads(resp)
	if not 'result' in data: return None
	if not 'version' in data['result']: return None
	return data['result']['version']
	
def toggleEnabled():
	version = getXBMCVersion()
	if not version or version['major'] < 13: return #Disabling in this manner crashes on Frodo
	base = '{ "jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.xbmc.tts","enabled":%s}, "id": 1 }'
	res = xbmc.executeJSONRPC(base % 'false') #Try to disable it
	if res and 'error' in res: #If we have an error, it's already disabled
		xbmc.executeJSONRPC(base % 'true') #So enable it instead
		
if __name__ == '__main__':
	toggleEnabled()