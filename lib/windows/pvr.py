# -*- coding: utf-8 -*-
import xbmc
import guitables
from base import WindowReaderBase

class PVRWindowReader(WindowReaderBase):
    ID = 'pvr'
    timelineInfo = (    u'Channel', #PVR
                        '$INFO[ListItem.ChannelNumber]',
                        '$INFO[ListItem.ChannelName]',
                        '$INFO[ListItem.StartTime]',
                        19160,
                        '$INFO[ListItem.EndTime]',
                        '$INFO[ListItem.Plot]'
    )
    
    channelInfo = (    '$INFO[ListItem.StartTime]',
                        19160,
                        '$INFO[ListItem.EndTime]',
                        '$INFO[ListItem.Plot]'
    )
    
    nowNextInfo = (    u'Channel',
                        '$INFO[ListItem.ChannelNumber]',
                        '$INFO[ListItem.ChannelName]',
                        '$INFO[ListItem.StartTime]',
                        '$INFO[ListItem.Plot]'
    )
    
    def init(self):
        self.mode = False
        
    def controlIsOnView(self,controlID):
        return controlID > 9 and controlID < 18
        
    def updateMode(self,controlID):
        if self.controlIsOnView(controlID):
            self.mode = 'VIEW'
        else:
            self.mode = None
        return self.mode
    
    def getControlDescription(self,controlID):
        old = self.mode
        new = self.updateMode(controlID)
        if new == None and old != None:
            return 'View Options'
        
    def getControlText(self,controlID):
        if not controlID: return (u'',u'')
        text = None
        if controlID == 11 or controlID == 12: #Channel (TV or Radio)
            text = '{0}... {1}... {2}'.format(xbmc.getInfoLabel('ListItem.ChannelNumber'),xbmc.getInfoLabel('ListItem.Label'),xbmc.getInfoLabel('ListItem.Title'))
        else:
            text = xbmc.getInfoLabel('System.CurrentControl')
        if not text: return (u'',u'')
        compare = text + xbmc.getInfoLabel('ListItem.StartTime') + xbmc.getInfoLabel('ListItem.EndTime')
        return (text.decode('utf-8'),compare)
        
    def getItemExtraTexts(self,controlID):
        text = None
        if self.controlIsOnView(controlID):
            if controlID == 10: #EPG: Timeline
                text = guitables.convertTexts(self.winID,self.timelineInfo)
            elif controlID == 11 or controlID == 12: #Channel (TV or Radio)
                text = guitables.convertTexts(self.winID,self.channelInfo)
            elif controlID == 16: #EPG: Now/Next
                text = guitables.convertTexts(self.winID,self.nowNextInfo)
        return text