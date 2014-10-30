# -*- coding: utf-8 -*-
from base import WindowReaderBase
import xbmc

class SettingsReader(WindowReaderBase):
    ID = 'settings'
    
    def getWindowExtraTexts(self):
        return None
        
    def getItemExtraTexts(self,controlID):
        text = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(controlID))
        if not text: return None
        return [text.decode('utf-8')]
        
    def getControlText(self,controlID):
        if not controlID: return (u'',u'')
        text = xbmc.getInfoLabel('System.CurrentControl')
        if not text: return (u'',u'')
        sub = u''
        if text.endswith(')'): #Skip this most of the time
                text = text.replace('( )','{0} no'.format(self.service.tts.pauseInsert)).replace('(*)','{0} yes'.format(self.service.tts.pauseInsert)) #For boolean settings
        if text.startswith('-'): sub = u'Sub-setting: '
        return (u'{0}{1}'.format(sub,text.decode('utf-8')),text)