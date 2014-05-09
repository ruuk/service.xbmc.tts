# -*- coding: utf-8 -*-
import xbmc

quartz = {	10000:
			{	301:{'name':20342,'prefix':u'section'}, #Movies
				302:{'name':20343,'prefix':u'section'}, #TV Shows
				303:{'name':2,'prefix':u'section'}, #Music
				304:{'name':1,'prefix':u'section'}, #Pictures
				305:{'name':24001,'prefix':u'section'}, #Addons
				306:{'name':'X B M C','prefix':u'section'},
				312:{'name':20387,'prefix':u'area'}, #Recently added tv shows
				313:{'name':359,'prefix':u'area'}, #Recently added albums
			}

}

skins = {	'quartz': quartz
}

CURRENT_SKIN_TABLE = None

def getControlText(winID,controlID):
	table = CURRENT_SKIN_TABLE
	if not table: return 
	if not  winID in table: return
	if not controlID in table[winID]: return
	label = table[winID][controlID]['name']
	if isinstance(label,int): label = xbmc.getLocalizedString(label)
	if not label: return
	if not 'prefix' in table[winID][controlID]: return label
	return u'{0}: {1}'.format(table[winID][controlID]['prefix'],label)


def getSkinTable():
	import os, xbmc
	skinPath = xbmc.translatePath('special://skin')
	skinName = os.path.basename(skinPath.rstrip('\/')).split('skin.',1)[-1]
	print 'service.xbmc.tts: SKIN: %s' % skinName
	return skins.get(skinName)

def updateSkinTable():
	global CURRENT_SKIN_TABLE
	CURRENT_SKIN_TABLE = getSkinTable()
	
updateSkinTable()