# -*- coding: utf-8 -*-
import os, hashlib, json
import xbmc
import util

DATAPATH = os.path.join(util.profileDirectory(),'addon_data.json')
BASE = '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": {"enabled": true,"properties": ["name","version"]}}'

def getAddonsMD5():
	return hashlib.md5(xbmc.executeJSONRPC(BASE)).hexdigest()

def saveAddonsMD5(md5):
	util.setSetting('addons_MD5',md5)

def loadAddonsMD5():
	return util.getSetting('addons_MD5')	

def initAddonsMD5():
	md5 = getAddonsMD5()
	saveAddonsMD5(md5)
	jsonString = xbmc.executeJSONRPC(BASE)
	with open(DATAPATH,'w') as f:
		f.write(jsonString)
	
def getAddonsDetails():
	data = json.loads(xbmc.executeJSONRPC(BASE))
	details = data[u'result'][u'addons']
	return details

def loadAddonsDetails(as_dict=False):
	if not os.path.exists(DATAPATH): return None
	data = json.loads(xbmc.executeJSONRPC(BASE))
	detailsList = data[u'result'][u'addons']
	if as_dict:  return dict((d['id'],d) for d in detailsList)
	return detailsList

def checkForNewVersions():
	last = loadAddonsMD5()
	new = getAddonsMD5()
	if last != new:
		saveAddonsMD5(new)
		return True
	return False

def getUpdatedAddons():
	details = loadAddonsDetails(as_dict=True)
	new = getAddonsDetails()
	ret = []
	for n in new:
		nid = n['addonid']
		if nid in details:
			if not n['version'] == details[nid]['version']:
				ret.append(n)
		else:
			ret.append(n)
	return ret