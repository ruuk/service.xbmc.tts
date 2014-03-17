# -*- coding: utf-8 -*-
import xbmc

'''
Table data format:
integer: XBMC localized string ID
string integer: controll ID
$INFO[<infolabel>]: infolabel
string: normal string
'''

winNames = {	10000: 10000,
				10001: 10001,
				10002: 10002,
				10003: 10003,
				10004: 10004,
				10005: 10005,
				10006: 10006,
				10007: 10007,
				10011: 10011,
				10012: 10012,
				10013: 10013,
				10014: 10014,
				10015: 10015,
				10016: 10016,
				10017: 10017,
				10018: 10018,
				10019: 10019,
				10020: 10020,
				10024: 10024,
				10025: 10025,
				10028: 10028,
				10029: 10029,
				10034: 10034,
				10040: 10040,
				10100: 10100,
				10101: 10101,
				10103: u'virtual keyboard',
				10104: u'volume bar',
				10106: u'context menu',
				10107: u'info dialog',
				10109: u'numeric input',
				10111: u'shutdown menu',
				10112: u'music scan',
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
				10130: 10034,
				10131: 20043,
				10132: 20333,
				10133: u'video scan',
				10134: 1036,
				10135: 658,
				10136: u'smart playlist editor',
				10137: 21421,
				10138: u'busy dialog',
				10139: 13406,
				10140: u'addon settings',
				10141: 1046,
				10142: u'fullscreen info',
				10143: u'karaoke selector',
				10144: u'karaoke large selector',
				10145: u'slider dialog',
				10146: u'addon information',
				10147: u'text viewer',
				10149: 35000,
				10150: u'peripheral settings',
				10151: 10101, #extended progress dialog - using string for progress dialog
				10152: u'media filter',
				10500: 20011,
				10501: 10501,
				10502: 10502,
				10503: 10503,
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
				12000: 12000,
				12001: 12001,
				12002: 12002,
				12003: 12003,
				12005: 12005,
				12006: 12006,
				12007: 108,
				12008: 12008,
				12009: 13327,
				12600: 12600,
				12900: 12900,
				12901: 12901,
				12902: u'video menu',
				12999: 512
}

winTexts = {	10100:('2','3','4'),
				12002:('2','3','4'),
				10103:('311',)

}

winExtraTexts = {	10000:(555,'$INFO[System.Time]',8,'$INFO[Weather.Temperature]','$INFO[Weather.Conditions]'),
					10146:(21863,'$INFO[ListItem.Property(Addon.Creator)]',19114,'$INFO[ListItem.Property(Addon.Version)]',21821,'$INFO[ListItem.Property(Addon.Description)]')

}

def getWindowName(winID):
	if not winID in winNames: return u''
	name = winNames[winID]
	if isinstance(name,int): name = xbmc.getLocalizedString(name)
	if not name: return u''
	return name or xbmc.getInfoLabel('System.CurrentWindow').decode('utf-8') or u'unknown'
	
def getWindowTexts(winID,table=winTexts):
	if not winID in table: return None
	ret = []
	for sid in table[winID]:
		if isinstance(sid,int):
			ret.append(xbmc.getLocalizedString(sid))
		elif sid.isdigit():
			ret.append(xbmc.getInfoLabel('Control.GetLabel({0})'.format(sid)).decode('utf-8'))
		elif sid.startswith('$INFO['):
			info = sid[6:-1]
			ret.append(xbmc.getInfoLabel(info).decode('utf-8'))
		else:
			ret.append(sid)
	return ret or None
	
def getExtraTexts(winID):
	return getWindowTexts(winID,table=winExtraTexts)
	
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