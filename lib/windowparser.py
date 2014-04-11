# -*- coding: utf-8 -*-
import xbmc, os, re
import bs4

def currentWindowXMLFile():
	base = xbmc.getInfoLabel('Window.Property(xmlfile)')
	if os.path.exists(base): return base
	path = getXBMCSkinPath(base)
	if os.path.exists(path): return path
	return None

def currentWindowIsAddon():
	path = xbmc.getInfoLabel('Window.Property(xmlfile)')
	if not path: return None
	return os.path.exists(path)
	
def getXBMCSkinPath(fname):
	path = os.path.join(xbmc.translatePath('special://skin'),'720p',fname)
	if os.path.exists(path): return path
	path = os.path.join(xbmc.translatePath('special://skin'),'1080i',fname)
	if os.path.exists(path): return path
	return getXBMCSkinPathCaseLowercase(fname)
	
def getXBMCSkinPathCaseLowercase(fname):
	fname = fname.lower()
	path = os.path.join(xbmc.translatePath('special://skin'),'720p',fname)
	if os.path.exists(path): return path
	path = os.path.join(xbmc.translatePath('special://skin'),'1080i',fname)
	if os.path.exists(path): return path
	return ''
	
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
			info = xbmc.getInfoLabel(parts[0]).decode('utf-8')
			if info:
				middle = parts[1] + info + parts[2]
			else:
				middle = ''
		elif len(parts) > 1:
			info = xbmc.getInfoLabel(parts[0]).decode('utf-8')
			if info:
				middle = parts[1] + info
			else:
				middle = ''
		else:
			middle = xbmc.getInfoLabel(middle).decode('utf-8')
			
		if middle: middle += '... '
		text = text[:pos] + middle + text[i+1:]
	return text.strip(' .')


class WindowParser:
	def __init__(self,xml_path):
		self.soup = bs4.BeautifulSoup(open(xml_path),'xml')
		self._listItemTexts = {}
		self.currentControl = None
		self.includes = None
		if not currentWindowIsAddon():
			self.processIncludes()
			import codecs
			with codecs.open(os.path.join(getXBMCSkinPath(''),'TESTCurrent.xml'),'w','utf-8') as f: f.write(self.soup.prettify())
		
	def processIncludes(self):
		self.includes = Includes()
		for i in self.soup.findAll('include'):
			condition = i.get('condition')
			if condition and not xbmc.getCondVisibility(condition):
				i.extract()
				continue
			matchingInclude = self.includes.getInclude(i.string)
			if not matchingInclude:
				#print 'INCLUDE NOT FOUND: %s' % i.string
				continue
			#print 'INCLUDE FOUND: %s' % i.string
			new = bs4.BeautifulSoup(unicode(matchingInclude),'xml').find('include')
			i.replace_with(new)
			new.unwrap()
			
	def addonReplacer(self,m):
		return xbmc.getInfoLabel(m.group(0)).decode('utf-8')
		
	def variableReplace(self,m):
		return self.includes.getVariable(m.group(1))
		
	def localizeReplacer(self,m):
		return xbmc.getLocalizedString(int(m.group(1)))
	
	def parseFormatting(self,text):
		text = tagRE.sub('',text).replace('[CR]','... ').strip(' .')
		text = varRE.sub(self.variableReplace,text)
		text = localizeRE.sub(self.localizeReplacer,text)
		text = addonRE.sub(self.addonReplacer,text)
		text = extractInfos(text)
		#text = infoLableRE.sub(self.infoReplacer,text)
		return text
	
	def getControl(self,controlID):
		return self.soup.find('control',{'id':controlID})
		
	def getLabelText(self,label):
		visible = label.find('visible',recursive=False)
		if visible and visible.string and not xbmc.getCondVisibility(visible.string): return None
		
		l = label.find('label')
		text = None
		if l: text = l.text
		if text:
			if text.isdigit(): text = '$LOCALIZE[{0}]'.format(text)
		else:
			i = label.find('info')
			if i:
				text = i.text
				if text.isdigit():
					text = '$LOCALIZE[{0}]'.format(text)
				else:
					text = '$INFO[{0}]'.format(text)
		if not text or text == '-':
			text = None
			if label.get('id'):
				#Nothing set for label. Try getting programatically set label.
				text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(label.get('id'))).decode('utf-8')
		if not text: return None
		return tagRE.sub('',text).replace('[CR]','... ').strip(' .')

	def processTextList(self,text_list):
		texts = []
		check = []
		for t in text_list:
			parsed = self.parseFormatting(t)
			if parsed and not t in check:
				texts.append(parsed)
				check.append(t)
		return texts
		
	def getListItemTexts(self,controlID):
		self.currentControl = controlID
		if controlID in self._listItemTexts:
			return self.processTextList(self._listItemTexts[controlID])
		#print controlID
		clist = self.getControl(controlID)
		if not clist: return None
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
			if not self.controlIsVisible(l): continue
			for p in l.parents:
				if not self.controlIsVisible(p): break
				if p.get('type') in ('list','fixedlist','wraplist','panel'): break
			else:
				text = self.getLabelText(l)
				if text and not text in texts: texts.append(text)
		return self.processTextList(texts)
		
	def controlIsVisible(self,control):
		visible = control.find('visible',recursive=False)
		if not visible: return True
		if not visible.string: return True
		if not xbmc.getCondVisibility(visible.string):
			return False
		else:
			return True
		
class Includes:
	def __init__(self):
		path = getXBMCSkinPath('Includes.xml')
		self.soup = bs4.BeautifulSoup(open(path),'xml')
		self._includesFilesLoaded = False
		self.includesMap = {}

	def loadIncludesFiles(self):
		if self._includesFilesLoaded: return
		basePath = getXBMCSkinPath('')
		for i in self.soup.find('includes').findAll('include'):
			xmlName = xbmc.validatePath(i.get('file'))
			if xmlName:
				p = os.path.join(basePath,xmlName)
				if not os.path.exists(p):
					continue
				soup =  bs4.BeautifulSoup(open(p),'xml')
				includes = soup.find('includes')
				i.replace_with(includes)
				for sub_i in includes.findAll('include'): self.includesMap[sub_i.get('name')] = sub_i
				includes.unwrap()
			else:
				self.includesMap[i.get('name')] = i
		self._includesFilesLoaded = True
		import codecs
		with codecs.open(os.path.join(getXBMCSkinPath(''),'Includes_Processed.xml'),'w','utf-8') as f: f.write(self.soup.prettify())
		
	def getInclude(self,name):
		self.loadIncludesFiles()
		return self.includesMap.get(name)
		#return self.soup.find('includes').find('include',{'name':name})
		
	def getVariable(self,name):
		var = self.soup.find('includes').find('variable',{'name':name})
		if not var: return ''
		for val in var.findAll('value'):
			condition = val.get('condition')
			if not condition:
				return val.string or ''
			else:
				if xbmc.getCondVisibility(condition):
					#print condition
					#print repr(val.string)
					return val.string or ''
		return ''
		
def getWindowParser():
	path = currentWindowXMLFile()
	if not path: return
	return WindowParser(path)