#!/usr/bin/python3

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from error_handling import handle_parsing_error
from voice.tts import *
import logging
logger = logging.getLogger('lib')

def bs4_iterate(soup):
	node = soup(recursive=False)[0]
	while node != None:
		sibling = node.nextSibling
		yield node
		node = sibling

		
class Parser:
	
	def parse(self):
		for node in bs4_iterate(self.soup):
			try:
				self._parse_node(node)
			except:
				handle_parsing_error(self, node)
				continue
				
	def load_attrs(self, attrs=None):
		if not attrs:
			attrs = self.soup.attrs
			assert attrs
		for k, v in attrs.items():
			logger.debug((k,v))
			if k in self.__dict__.keys():
				logger.warning(f'Unsafe XML attribute {k}="{v}"')
			else:
				self.__dict__[k] = v
				
	def _parse_node(self, node):
		raise NotImplementedError

class SceneParser(Parser):
	actions = []
	def __init__(self, node, parent):
		assert str(node.name) == 'scene', f'Content {node.name} outside of scene:\n{self}'
		self.parent = parent
		self.soup = node
		attrs = {**parent.soup.attrs, **node.attrs}
		self.load_attrs(attrs=attrs)
		voice_class = globals().get(attrs.get('voice', None), GttsVoice)
		self.voice = voice_class(lang=attrs.get('lang','en'))
		self.parse()
			
	def _parse_node(self, node):
		if type(node) == NavigableString and str(node.string).strip():
			node.insert_before(BeautifulSoup(f'<tts>{node.string}</tts>','lxml-xml'))
			node = node.previousSibling	
		if node.name:
			self.actions.append(node)
		
class PlaybookParser(Parser):
	scenes = []
	def __init__(self, path):
		self.path = path
		self.load(path)
		self.load_attrs()
		self.parse()
		
	def load(self, path):
		with open(path) as fp:
			self.soup = BeautifulSoup(fp.read(), 'xml').playbook
				
	def _parse_node(self, node):
		if node and node.name == 'scene':
			self.scenes.append(SceneParser(node, self))
		
if __name__=='__main__':
	STRICT = False
	pb = PlaybookParser('playbook.xml')
	print('\n'.join(['\n'.join([f'''
{COLOR%YELLOW}<action type="{action.name}">{END}
{action}
{COLOR%YELLOW}</action>{END}
	'''for action in scene.actions]) for scene in pb.scenes]))

	
	

		
