# -*- coding: utf-8 -*-
import xbmc, re, difflib, time
from base import WindowReaderBase

class VirtualKeyboardReader(WindowReaderBase):
    ID = 'virtualkeyboard'
    ip_re = re.compile('^[\d ]{3}\.[\d ]{3}\.[\d ]{3}.[\d ]{3}$')
        
    def init(self):
        self.editID = None
        if self.winID == 10103:
            self.editID = 310
        elif self.winID == 10109:
            self.editID = 4
        self.keyboardText = ''
        self.lastChange = time.time()
        self.lastRead = None
            
    def getHeading(self): xbmc.getInfoLabel('Control.GetLabel(311)'.decode('utf-8'))
    
    def isIP(self,text=None):
        text = text or self.getEditText()
        return self.winID == 10109 and '.' in text #Is numeric input with . in it, so must be IP

    def getEditText(self):
        return xbmc.getInfoLabel('Control.GetLabel({0})'.format(self.editID)).decode('utf-8')
        
    def getMonitoredText(self,isSpeaking=False):
        text = self.getEditText()
        if text != self.keyboardText:
            self.lastChange = time.time()
            out = ''
            d = difflib.Differ()
            if not text:
                out = u'No text'
            elif self.isIP(text):
                if self.isIP(text) and self.isIP(self.keyboardText): #IP Address
                    oldip = self.keyboardText.replace(' ','').split('.')
                    newip = text.replace(' ','').split('.')
                    for old,new in zip(oldip,newip):
                        if old == new: continue
                        out = ' '.join(list(new))
                        break
            elif len(text) > len(self.keyboardText):
                for c in d.compare(self.keyboardText,text):
                    if c.startswith('+'):
                        out += u' ' + (c.strip(' +') or 'space')
            else:
                for c in d.compare(self.keyboardText,text):
                    if c.startswith('-'): out += u' ' + (c.strip(' -') or 'space')
                if out: out = out.strip() + ' deleted'
            self.keyboardText = text
            if out:
                return out.strip()
        else:
            now = time.time()
            if now - self.lastChange > 2: #We haven't had input for a second, read all the text
                if text != self.lastRead:
                    self.lastChange = now
                    self.lastRead = text
                    if self.isIP(text): return text.replace(' ','')
                    return text
        return None