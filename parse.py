#!/usr/bin/python3

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from error_handling import handle_parsing_error
from voice.tts import *
import logging
logger = logging.getLogger('lib')

def scene_iterate(soup):
	"""
	>>> list(scene_iterate(BeautifulSoup('<a><b>1</b><b>2</b></a><c>3</c>').a))
	[<b>1</b>, <b>2</b>]	
	"""
	node = soup(recursive=False)[0]
	while node != None:
		assert node.parent == soup
		#print(node)
		#print('*'*50)
		if node.name == 'scene':
			break
		yield node
		sibling = node.nextSibling
		node = sibling

class Parser:	
	def _try_parse_node(self, node):
		try:
			self._parse_node(node)
		except:
			handle_parsing_error(self, node)
				
	def load_attrs(self, attrs=None):
		if attrs == None:
			attrs = self.soup.attrs
			assert attrs
			logger.debug(attrs)
		for k, v in attrs.items():
			logger.debug((k,v))
			if k in self.__dict__.keys():
				logger.warning(f'Unsafe XML attribute {k}="{v}"')
			else:
				self.__dict__[k] = v
				
	def _parse_node(self, node):
		raise NotImplementedError
		
	def parse(self):
		pass

  
class SceneParser(Parser):
	def __init__(self, node, parent):
		assert str(node.name) == 'scene', f'Content {node.name} outside of scene:\n{self}'
		self.parent = parent
		self.soup = node
		attrs = {**parent.soup.attrs, **node.attrs}
		self.load_attrs(attrs=attrs)
		self.voice = GttsVoice(lang='en-uk') # DEFAULT
		self.actions = []
		self.parse()
			
	def _parse_node(self, node):
		assert node.parent == self.soup #DEBUG
		if type(node) == NavigableString and str(node.string).strip():
			node.insert_before(BeautifulSoup(f'<tts>{node.string}</tts>','lxml-xml'))
			node = node.previousSibling	
		if node.name:
			self.actions.append(node)
			
	def parse(self):
		#print(self.actions)	
		for node in scene_iterate(self.soup):
			self._try_parse_node(node)
		#print(self.actions)
			
class PlaybookParser(Parser):
	scenes = []
	actions = []
	def __init__(self, path):
		self.path = path
		self.load(path)
		self.load_attrs()
		self.parse()
		
	def load(self, path):
		with open(path) as fp:
			self.soup = BeautifulSoup(fp.read(), 'lxml-xml').playbook
				
	def _parse_node(self, node):
		if node and node.name == 'scene':
			self.scenes.append(SceneParser(node, self))
		else:
			self.actions.append(node)
		
	def parse(self):
		for node in self.soup.findChildren(recursive=False):
			#print('>'*50)
			#print(node)
			self._try_parse_node(node)
		
if __name__=='__main__':
	STRICT = False
	pb = PlaybookParser('playbook.xml')
	print('\n'.join(['\n'.join([f'''
{COLOR%YELLOW}<action type="{action.name}">{END}
{action}
{COLOR%YELLOW}</action>{END}
	'''for action in scene.actions]) for scene in pb.scenes]))

	
	

		
