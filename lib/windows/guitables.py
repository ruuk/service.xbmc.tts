# -*- coding: utf-8 -*-
import os, re, codecs, xbmc

'''
Table data format:
integer: XBMC localized string ID
string integer: controll ID
$INFO[<infolabel>]: infolabel
string: normal string
'''

winNames = {		10000: 10000, #Home
				10001: 10001, #programs
				10002: 10002, #pictures
				10003: 10003, #filemanager
				10004: 10004, #settings
				10005: 10005, #music
				10006: 10006, #video
				10007: 10007, #systeminfo
				10011: 10011, #screencalibration
				10012: 10012, #picturessettings
				10013: 10013, #programssettings
				10014: 10014, #weathersettings
				10015: 10015, #musicsettings
				10016: 10016, #systemsettings
				10017: 10017, #videossettings
				10018: 10018, #servicesettings
				10019: 10019, #appearancesettings
				10020: 10020, #scripts
				10024: 10024, #videofiles: Removed in Gotham
				10025: 10025, #videolibrary
				10028: 10028, #videoplaylist
				10029: 10029, #loginscreen
				10034: 10034, #profiles
				10040: 10040, #addonbrowser
				10100: 10100, #yesnodialog
				10101: 10101, #progressdialog
				10103: u'virtual keyboard',
				10104: u'volume bar',
				10106: u'context menu',
				10107: u'info dialog',
				10109: u'numeric input',
				10111: u'shutdown menu',
				10113: u'mute bug',
				10114: u'player controls',
				10115: u'seek bar',
				10120: u'music OSD',
				10122: u'visualisation preset list',
				10123: u'OSD video settings',
				10124: u'OSD audio settings',
				10125: u'video bookmarks',
				10126: u'file browser',
				10128: u'network setup',
				10129: u'media source',
				10130: 10034, #profilesettings
				10131: 20043, #locksettings
				10132: 20333, #contentsettings
				10134: 1036, #favourites
				10135: 658, #songinformation
				10136: u'smart playlist editor',
				10137: 21421, #smartplaylistrule
				10138: u'busy dialog',
				10139: 13406, #pictureinfo
				10140: u'addon settings',
				10141: 1046, #accesspoints
				10142: u'fullscreen info',
				10143: u'karaoke selector',
				10144: u'karaoke large selector',
				10145: u'slider dialog',
				10146: u'addon information',
				10147: u'text viewer',
				10149: 35000, #peripherals
				10150: u'peripheral settings',
				10151: 10101, #extended progress dialog - using string for progress dialog
				10152: u'media filter',
				10500: 20011, #musicplaylist
				10501: 10501, #musicfiles
				10502: 10502, #musiclibrary
				10503: 10503, #musicplaylisteditor
				10601: u'pvr',
				10602: u'pvr guide info',
				10603: u'pvr recording info',
				10604: u'pvr timer setting',
				10605: u'pvr group manager',
				10606: u'pvr channel manager',
				10607: u'pvr guide search',
				10610: u'pvr OSD channels',
				10611: u'pvr OSD guide',
				11000: u'virtual keyboard',
				12000: 12000, #selectdialog
				12001: 12001, #musicinformation
				12002: 12002, #okdialog
				12003: 12003, #movieinformation
				12005: 12005, #fullscreenvideo
				12006: 12006, #visualisation
				12007: 108, #slideshow
				12008: 12008, #filestackingdialog
				12009: 13327, #karaoke
				12600: 12600, #weather
				12900: 12900, #screensaver
				12901: 12901, #videoosd
				12902: u'video menu',
				12999: 512 #startup
}

winTexts = {	10100:('2','3','4','9'), #Yes/No Dialog - 1,2,3=Older Skins 9=Newer Skins
				12002:('2','3','4','9') #OK Dialog - 1,2,3=Older Skins 9=Newer Skins
}

winExtraTexts = {	10000:(555,'$INFO[System.Time]',8,'$INFO[Weather.Temperature]','$INFO[Weather.Conditions]'), #Home
					10146:(	21863, #Addon Info Dialog
							'$INFO[ListItem.Property(Addon.Creator)]',
							19114,
							'$INFO[ListItem.Property(Addon.Version)]',
							21821,'$INFO[ListItem.Property(Addon.Description)]'
					),
					10147:('textbox',) #Text Viewer
					
}

itemExtraTexts = {	}

winListItemProperties = {		10040:('$INFO[ListItem.Property(Addon.Status)]',)

}
	
def textviewerText(winID):
	folderPath = xbmc.getInfoLabel('Container.FolderPath')
	if folderPath.startswith('addons://'):
		changelog = os.path.join(xbmc.getInfoLabel('ListItem.Property(Addon.Path)'),'changelog.txt')
		if not os.path.exists(changelog): return None
		ret = []
		with codecs.open(changelog,'r','utf-8') as f:
			lines = f.readlines()
		for l in lines:
			if not re.search('\w',l): continue
			ret.append(l.strip())
		return ret
	return None

textboxTexts = { 10147:{'type':'function','function':textviewerText}

}

def getTextBoxTexts(winID):
	if not winID in textboxTexts: return None
	info = textboxTexts[winID]
	if info['type'] == 'function':
		return info['function'](winID)
	return None
	
def getWindowAddonID(winID):
	path = xbmc.getInfoLabel('Window({0}).Property(xmlfile)'.format(winID)).decode('utf-8')
	addonID = path.split('/addons/',1)[-1].split('/',1)[0]
	return addonID

def getWindowAddonName(winID):
	addonID = getWindowAddonID(winID)
	return xbmc.getInfoLabel('System.AddonTitle({0})'.format(addonID)) or addonID

def getWindowName(winID):
	name = None
	if winID in winNames:
		name = winNames[winID]
		if isinstance(name,int): name = xbmc.getLocalizedString(name)
	elif winID > 12999:
		return getWindowAddonName(winID)
	return name or xbmc.getInfoLabel('System.CurrentWindow').decode('utf-8') or u'unknown'
	
def convertTexts(winID,data_list):
	ret = []
	for sid in data_list:
		if isinstance(sid,int):
			sid = xbmc.getLocalizedString(sid)
		elif sid.isdigit():
			sid = xbmc.getInfoLabel('Control.GetLabel({0})'.format(sid)).decode('utf-8')
		elif sid == 'textbox':
			texts = getTextBoxTexts(winID)
			if texts:
				ret += texts
				continue
		elif sid.startswith('$INFO['):
			info = sid[6:-1]
			sid = xbmc.getInfoLabel(info).decode('utf-8')
		if sid: ret.append(sid)
	return ret
			
def getWindowTexts(winID,table=winTexts):
	if not winID in table: return None
	return convertTexts(winID,table[winID]) or None
	
def getExtraTexts(winID):
	return getWindowTexts(winID,table=winExtraTexts)
	
def getItemExtraTexts(winID):
	return getWindowTexts(winID,table=itemExtraTexts)

def getListItemProperty(winID):
	texts = getWindowTexts(winID,table=winListItemProperties)
	if not texts: return None
	return u','.join(texts)

def getSongInfo():
	if xbmc.getCondVisibility('ListItem.IsFolder'): return None
	title = xbmc.getInfoLabel('ListItem.Title')
	genre = xbmc.getInfoLabel('ListItem.Genre')
	duration = xbmc.getInfoLabel('ListItem.Duration')
	if not (title or genre or duration): return None
	ret = []
	if title:
		ret.append(xbmc.getLocalizedString(556))
		ret.append(title.decode('utf-8'))
	if genre:
		ret.append(xbmc.getLocalizedString(515))
		ret.append(genre.decode('utf-8'))
	if duration:
		ret.append(xbmc.getLocalizedString(180))
		ret.append(duration.decode('utf-8'))
	return ret

