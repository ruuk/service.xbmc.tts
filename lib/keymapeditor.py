# -*- coding: utf-8 -*-
import os
from threading import Timer
import xbmc, xbmcgui, xbmcaddon
import util

ACTIONS = (
			('REPEAT','f1'),
			('EXTRA','f2'),
			('ITEM_EXTRA','f3'),
			('STOP','f4'),
			('SETTINGS','f6'),
			('DISABLE','f12'),
			('VOL_UP','numpadplus mod="ctrl"'),
			('VOL_DOWN','numpadminus mod="ctrl"')

)

def processCommand(command):
	if command == 'INSTALL_DEFAULT':
		installDefaultKeymap()
	elif command == 'INSTALL_CUSTOM':
		installCustomKeymap()
	elif command == 'EDIT':
		editKeymap()
	elif command == 'RESET':
		resetKeymap()
	elif command == 'REMOVE':
		removeKeymap()

def _keymapTarget():
	return os.path.join(xbmc.translatePath('special://userdata').decode('utf-8'),'keymaps','service.xbmc.tts.keyboard.xml')
	
def _keymapSource():
	return os.path.join(xbmc.translatePath(xbmcaddon.Addon(util.ADDON_ID).getAddonInfo('path')).decode('utf-8'),'resources','keymap.base.xml')

def _keyMapDefsPath():
	return os.path.join(xbmc.translatePath(xbmcaddon.Addon(util.ADDON_ID).getAddonInfo('profile')).decode('utf-8'),'custom.keymap.defs')

def loadCustomKeymapDefs():
	path = _keyMapDefsPath()
	if not os.path.exists(path): return {}
	with open(path,'r') as f:
		lines = f.read().splitlines()
	defs = {}
	try:
		for l in lines:
			if not l: continue
			key,val = l.split("=",1)
			defs[key] = val
		return defs
	except:
		util.ERROR('Error reading custom keymap definitions')
	return {}
	
def saveCustomKeymapDefs(defs):
	out = ''
	for k,v in defs.items():
		out += '{0}={1}\n'.format(k,v)
	path = _keyMapDefsPath()
	with open(path,'w') as f:
		f.write(out)
	
def installDefaultKeymap():
	buildKeymap(defaults=True)
	xbmcgui.Dialog().ok('Installed','Default keymap installed successfully!')

def installCustomKeymap():
	buildKeymap()
	xbmcgui.Dialog().ok('Updated','Custom keymap installed or updated successfully!')

def resetKeymap():
	saveCustomKeymapDefs({})
	buildKeymap()
	xbmcgui.Dialog().ok('Updated','Custom keymap reset to defaults.')
	
def removeKeymap():
	targetPath = _keymapTarget()
	import xbmcvfs
	if os.path.exists(targetPath):
		xbmcvfs.delete(targetPath)
	xbmc.executebuiltin("action(reloadkeymaps)")
	xbmcgui.Dialog().ok('Removed','Keymap removed.')

def saveKeymapXML(xml):
	import xbmcvfs
	targetPath = _keymapTarget()
	if os.path.exists(targetPath): xbmcvfs.delete(targetPath)
	with open(targetPath,'w') as f:
		f.write(xml)
	xbmc.executebuiltin("action(reloadkeymaps)")
	
def buildKeymap(defaults=False): #TODO: Build XML with ElementTree?
	xml = None
	with open(_keymapSource(),'r') as f:
		xml = f.read()
	if not xml: return
	if defaults:
		defs = {}
	else:
		defs = loadCustomKeymapDefs()
	for action, default in ACTIONS:
		key = defs.get('key.{0}'.format(action))
		if key:
			xml = xml.replace('<{0}>'.format(action),'<key id="{0}">'.format(key)).replace('</{0}>'.format(action),'</key>')
		else:
			xml = xml.replace('<{0}>'.format(action),'<{0}>'.format(default)).replace('</{0}>'.format(action),'</{0}>'.format(default.split(' ',1)[0]))
	saveKeymapXML(xml)

def editKeymap():
	options = (
					('Repeat Control ({0})','key.REPEAT'),
					('Window Extra Info ({0})','key.EXTRA'),
					('Item Extra Info ({0})','key.ITEM_EXTRA'),
					('Stop Speech ({0})','key.STOP'),
					('Addon Settings ({0})','key.SETTINGS'),
					('Disable/Enable TTS Addon ({0})','key.DISABLE'),
					('Volume Up ({0})','key.VOL_UP'),
					('Volume Down ({0})','key.VOL_DOWN')
	)

	while True:
		defs = loadCustomKeymapDefs()
		items = []
		for i,ID in options:
			items.append(i.format(defs.get(ID) or 'Not Set'))
			
		idx = xbmcgui.Dialog().select('Actions',items)
		if idx < 0: return
		ID = options[idx][1]
		editKey(ID,defs)

def editKey(key_id,defs):
	key = KeyListener.record_key()
	if not key: return
	util.notifySayText('Key set',interrupt=True)
	defs[key_id] = key
	saveCustomKeymapDefs(defs)

# Taken from takoi's Keymap Editor
class KeyListener(xbmcgui.WindowXMLDialog):
	TIMEOUT = 60

	def __new__(cls):
					return super(KeyListener, cls).__new__(cls, "DialogKaiToast.xml", "")

	def __init__(self):
		self.msg1 = 'Press the key you want to assign now.'
		self.msg2 = 'Timeout in %.0f seconds...' % self.TIMEOUT
		self.key = None

	def onInit(self):
		try:
			self.getControl(401).addLabel(self.msg1)
			self.getControl(402).addLabel(self.msg2)
		except AttributeError:
			self.getControl(401).setLabel(self.msg1)
			self.getControl(402).setLabel(self.msg2)
		externalWindowObj = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
		externalWindowObj.setProperty('TTS.READER','keymapkeyinput')

	def onAction(self, action):
		if action == 9 or action == 10 or action == 92:
			self.close()
		else:
			code = action.getButtonCode()
			self.key = None if code == 0 else str(code)
			self.close()

	@staticmethod
	def record_key():
		dialog = KeyListener()
		timeout = Timer(KeyListener.TIMEOUT, dialog.close)
		timeout.start()
		dialog.doModal()
		timeout.cancel()
		key = dialog.key
		del dialog
		return key