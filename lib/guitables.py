# -*- coding: utf-8 -*-
import xbmc

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
				10103: 'virtual keyboard',
				10104: 'volume bar',
				10106: 'context menu',
				10107: 'info dialog',
				10109: 'numeric input',
				10111: 'shutdown menu',
				10112: 'music scan',
				10113: 'mute bug',
				10114: 'player controls',
				10115: 'seek bar',
				10120: 'music OSD',
				10122: 'visualisation preset list',
				10123: 'OSD video settings',
				10124: 'OSD audio settings',
				10125: 'video bookmarks',
				10126: 'file browser',
				10128: 'network setup',
				10129: 'media source',
				10130: 10034,
				10131: 20043,
				10132: 20333,
				10133: 'video scan',
				10134: 1036,
				10135: 658,
				10136: 'smart playlist editor',
				10137: 21421,
				10138: 'busy dialog',
				10139: 13406,
				10140: 'addon settings',
				10141: 1046,
				10142: 'fullscreen info',
				10143: 'karaoke selector',
				10144: 'karaoke large selector',
				10145: 'slider dialog',
				10146: 'addon information',
				10147: 'text viewer',
				10149: 35000,
				10150: 'peripheral settings',
				10151: 10101, #extended progress dialog - using string for progress dialog
				10152: 'media filter',
				10500: 20011,
				10501: 10501,
				10502: 10502,
				10503: 10503,
				10601: 'pvr',
				10602: 'pvr guide info',
				10603: 'pvr recording info',
				10604: 'pvr timer setting',
				10605: 'pvr group manager',
				10606: 'pvr channel manager',
				10607: 'pvr guide search',
				10610: 'pvr OSD channels',
				10611: 'pvr OSD guide',
				11000: 'virtual keyboard',
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
				12902: 'video menu',
				12999: 512
}

winTexts = {	10100:(2,3,4),
				12002:(2,3,4)

}

def getWindowName(winID):
	if not winID in winNames: return ''
	name = winNames[winID]
	if isinstance(name,int): name = xbmc.getLocalizedString(name)
	if not name: return ''
	return name
	
def getWindowTexts(winID):
	if not winID in winTexts: return None
	ret = []
	for cid in winTexts[winID]:
		ret.append(xbmc.getInfoLabel('Control.GetLabel({0})'.format(cid)))
	return ret or None