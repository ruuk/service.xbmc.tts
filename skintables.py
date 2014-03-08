# -*- coding: utf-8 -*-

quartz = {	10000:
			{	301:{'name':'movies','prefix':'section'},
				302:{'name':'T V Shows','prefix':'section'},
				303:{'name':'music','prefix':'section'},
				304:{'name':'pictures','prefix':'section'},
				305:{'name':'add-ons','prefix':'section'},
				306:{'name':'X B M C','prefix':'section'},
				312:{'name':'recently added episodes','prefix':'area'},
				313:{'name':'recently added albums','prefix':'area'},
			}

}

skins = {	'quartz': quartz
}

def getSkinTable():
	import os, xbmc
	skinPath = xbmc.translatePath('special://skin')
	skinName = os.path.basename(skinPath.rstrip('\/')).split('skin.',1)[-1]
	print 'service.xbmc.tts: SKIN: %s' % skinName
	return skins.get(skinName)