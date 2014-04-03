# -*- coding: utf-8 -*-
import xbmc, os, re
import bs4

def currentWindowXMLFile():
	base = xbmc.getInfoLabel('Window.Property(xmlfile)')
	if os.path.exists(base): return base
	path = os.path.join(xbmc.translatePath('special://skin'),'720p',base)
	if os.path.exists(path): return path
	path = os.path.join(xbmc.translatePath('special://skin'),'1080i',base)
	if os.path.exists(path): return path
	return None


tagRE = re.compile(r'\[/?(?:B|I|COLOR|UPPERCASE|LOWERCASE)[^\]]*\](?i)')
varRE = re.compile(r'\$VAR\[([^\]]*)\]')
localizeRE = re.compile(r'\$LOCALIZE\[([^\]]*)\]')
addonRE = re.compile(r'\$ADDON\[[\w+\.]+ (\d+)\]')
infoLableRE = re.compile(r'\$INFO\[([^\]]*)\]')

def extractInfos(text):
	pos = 0
	while pos > -1:
		pos = text.find('$INFO[')
		if pos < 0: break
		pos 
		lbracket = pos + 6
		i = lbracket
		depth = 1
		for c in text[pos + 6:]:
			if c == '[':
				depth+=1
			elif c == ']':
				depth-=1
			if depth < 1: break
			i+=1
		middle = text[lbracket:i]
		
		parts = middle.split(',')
		if len(parts) > 2:
			middle = parts[1] + xbmc.getInfoLabel(parts[0]) + parts[2]
		elif len(parts) > 1:
			middle = parts[1] + xbmc.getInfoLabel(parts[0])
		else:
			middle = xbmc.getInfoLabel(middle)
			
		if middle: middle += '... '
		text = text[:pos] + middle + text[i+1:]
	return text


class WindowParser:
	def __init__(self,xml_path):
		self.soup = bs4.BeautifulSoup(open(xml_path),'xml')
		self._listItemTexts = {}
		self.currentControl = None
		
	def addonReplacer(self,m):
		return xbmc.getInfoLabel(m.group(0))
		
	def localizeReplacer(self,m):
		return xbmc.getLocalizedString(m.group(1))
		
	def infoReplacer(self,m):
		info = m.group(1)
		if info.lower().startswith('listitem.') and self.currentControl:
			info = 'Container({0}).{1}'.format(self.currentControl,info)
		parts = info.split(',')
		print info
		if len(parts) > 2:
			info = parts[1] + xbmc.getInfoLabel(parts[0]) + parts[2]
		elif len(parts) > 1:
			info = parts[1] + xbmc.getInfoLabel(parts[0])
		else:
			info = xbmc.getInfoLabel(info)
		print info
		return info
	
	def parseFormatting(self,text):
		text = tagRE.sub('',text).replace('[CR]','... ')
		text = varRE.sub('',text) #TODO: Actually process the variable
		text = localizeRE.sub(self.localizeReplacer,text)
		text = addonRE.sub(self.addonReplacer,text)
		text = extractInfos(text)
		#text = infoLableRE.sub(self.infoReplacer,text)
		return text
	
	def getControl(self,controlID):
		return self.soup.find('control',{'id':controlID})
		
	def getLabelText(self,label):
		l = label.find('label')
		text = None
		if l: text = l.text
		if not text:
			i = label.find('info')
			if i:
				text = i.text
				if text.isdigit():
					text = '$LOCALIZE[{0}]'.format(text)
				else:
					text = '$INFO[{0}]'.format(text)
		if not text: return None
		return tagRE.sub('',text).replace('[CR]','... ').strip()

	def processTextList(self,text_list):
		texts = []
		for t in text_list:
			parsed = self.parseFormatting(t)
			if parsed: texts.append(parsed)
		return texts
		
	def getListItemTexts(self,controlID):
		self.currentControl = controlID
		if controlID in self._listItemTexts:
			return self.processTextList(self._listItemTexts[controlID])
		print controlID
		clist = self.getControl(controlID)
		fl = clist.find("focusedlayout")
		if not fl: return None
		lt = fl.findAll('control',{'type':('label','textbox')})
		texts = []
		for l in lt:
			text = self.getLabelText(l)
			if text and not text in texts: texts.append(text)
		self._listItemTexts[controlID] = texts
		return self.processTextList(texts)
			
	def getWindowTexts(self):
		lt = self.soup.findAll('control',{'type':('label','textbox')})
		texts = []
		for l in lt:
			for p in l.parents:
				if p.name in ('list','fixedlist','wraplist','panel'): break
			else:
				text = self.getLabelText(l)
				if text and not text in texts: texts.append(text)
		return self.processTextList(texts)
			
def getWindowParser():
	path = currentWindowXMLFile()
	if not path: return
	return WindowParser(path)