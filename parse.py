#!/usr/bin/python3

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from error_handling import handle_parsing_error
from voice.tts import *
import logging
logger = logging.getLogger('lib')

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
		for node in self.soup.findChildren(recursive=False):
			print(node)
			print('-'*50)
			self._try_parse_node(node)

  
class SceneParser(Parser):
	def __init__(self, node, parent):
		assert str(node.name) == 'scene', f'Content {node.name} outside of scene:\n{self}'
		self.parent = parent
		self.soup = node
		attrs = {**parent.soup.attrs, **node.attrs}
		self.load_attrs(attrs=attrs)
		self.voice = GttsVoice(lang='en-uk') # DEFAULT
		self.actions = [] #parent.actions #TODO: try copy()/deepcopy()
		self.parse()
			
	def _parse_node(self, node):
		if node.name:
			self.actions.append(node)
			
class PlaybookParser(Parser):
	def __init__(self, path):
		self.scenes = []
		self.actions = []
		self.path = path
		self.load(path)
		self.load_attrs()
		self.parse()
		
	def load(self, path):
		with open(path) as fp:
			self.soup = BeautifulSoup(fp.read(), 'lxml-xml').playbook
				
	def _parse_node(self, node):
		if node.name == 'scene':
			if node(recursive=False):
				self.scenes.append(SceneParser(node, self))
		else:
			self.actions.append(node)
		
if __name__=='__main__':
	STRICT = False
	pb = PlaybookParser('playbook.xml')
	print('\n'.join(['\n'.join([f'''
{COLOR%YELLOW}<action type="{action.name}">{END}
{action}
{COLOR%YELLOW}</action>{END}
	'''for action in scene.actions]) for scene in pb.scenes]))

	
	

		
