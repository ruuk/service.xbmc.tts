# -*- coding: utf-8 -*-
import xbmc

quartz = {	10000:
			{	301:{'name':20342,'prefix':'section'}, #Movies
				302:{'name':20343,'prefix':'section'}, #TV Shows
				303:{'name':2,'prefix':'section'}, #Music
				304:{'name':1,'prefix':'section'}, #Pictures
				305:{'name':24001,'prefix':'section'}, #Addons
				306:{'name':'X B M C','prefix':'section'},
				312:{'name':20387,'prefix':'area'}, #Recently added tv shows
				313:{'name':359,'prefix':'area'}, #Recently added albums
			}

}

skins = {	'quartz': quartz
}

def getControlText(table,winID,controlID):
	if not table: return 
	if not  winID in table: return
	if not controlID in table[winID]: return
	label = table[winID][controlID]['name']
	if isinstance(label,int): label = xbmc.getLocalizedString(label).encode('utf8')
	if not label: return ''
	if not 'prefix' in table[winID][controlID]: return label
	return '{0}: {1}'.format(table[winID][controlID]['prefix'],label)


def getSkinTable():
	import os, xbmc
	skinPath = xbmc.translatePath('special://skin')
	skinName = os.path.basename(skinPath.rstrip('\/')).split('skin.',1)[-1]
	print 'service.xbmc.tts: SKIN: %s' % skinName
	return skins.get(skinName)
