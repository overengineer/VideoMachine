#!/usr/bin/python3

from bs4 import BeautifulSoup
from bs4.element import NavigableString
import sys, traceback, logging
from snippets.snippet import Snippet
from moviepy.editor import ImageClip, AudioFileClip, concatenate_audioclips
from voice.tts import Voice

def bs4_iterate(soup):
	node = soup(recursive=False)[0]
	while node != None:
		sibling = node.nextSibling
		yield node
		node = sibling

RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(31,38)
END = "\033[0m"
COLOR = "\033[1;%dm"

def handle_parsing_error(parser, node):	
	msg = f'''Parsing "{node.name}" in "{parser.soup.name}" failed
	{COLOR%YELLOW}{node}{END}
	{COLOR%RED}{traceback.format_exc()}{END}'''
	if globals().get('STRICT', False):
		logging.error(msg)
		sys.exit(-1)
	else:
		logging.warning(msg)
		
class Parser:
	def parse(self):
		for node in bs4_iterate(self.soup):
			try:
				self._parse_node(node)
			except:
				handle_parsing_error(self, node)
				continue
				
	def _parse_node(self, node):
		pass

class Scene(Parser):
	actions = []
	def __init__(self, node):
		assert str(node.name) == 'scene', f'Content {node.name} outside of scene:\n{self}'
		self.soup = node
		self.parse()
			
	def _parse_node(self, node):
		if type(node) == NavigableString and str(node.string).strip():
			node.insert_before(BeautifulSoup(f'<tts>{node.string}</tts>','lxml-xml'))
			node = node.previousSibling	
		if node.name:
			self.actions.append(node)
		
class Playbook(Parser):
	scenes = []
	def __init__(self, path):
		self.path = path
		self.load(path)
		self.parse()
		
	def load(self, path):
		with open(path) as fp:
			self.soup = BeautifulSoup(fp.read(), 'xml').playbook
				
	def _parse_node(self, node):
		if node and node.name:
			self.scenes.append(Scene(node))


# write a decorater as a classmethod of playbook that register scene classes
class CodingScene(Scene):
	clips = []
	sounds = []
	images = []
	hl_lines = []
	snippet = None
	
	def __init__(self, voice=None):
		self.voice = voice or Voice(octave=5, speed=1.25)
		
	def code(self, node):
		text = str(node.string)
		self.snippet = Snippet(text)
		self._push_snippet()
		assert self.snippet == None, "code tag placed in the scene twice"
		
	def _push_snippet(self):
		image = self.snippet.to_image()
		self._push_image(image)
		
	def _push_sound_file(self, path):
		sound = AudioFileClip(path)
		self.sounds.append(sound)
		
	def _push_image(self, image):
		clip = ImageClip(image)
		self.images.append(image)
		
	def _compose_buffer(self):
		audio = CompositeAudioClip(sounds)
		video = CompositeVideoClip(images, duration=sound.duration)
		video.set_audio(audio)
		clips.append(video)
		sounds, images = [], []
		
	def hl(self, node):
		lines = [int(s) for s in node.attrs.get('hl_lines', '').split()]
		# Update Snippet
		if self.hl_lines != lines:
			self._compose_buffer()
			self.hl_lines = lines
			image = self.snippet.to_image(hl_lines=lines)
			self._push_image(image)
		# tts & reset hl
		if not node.isSelfClosing:
			text = str(node.string)
			self.tts(text)
			self.hl_lines = []
		
	def tts(self, txt):
		path = self.voice.say(txt)
		self._push_sound_file(path)
				
	def wait(self, node):
		silence = AudioClip(lambda t: 0, duration=node.attrs['sec'])
		self.sounds.append(silence)
		
		
if __name__=='__main__':
	STRICT = True
	pb = Playbook('playbook.xml')
	print('\n'.join(['\n'.join([f'''
{COLOR%YELLOW}<action type="{action.name}">{END}
{action}
{COLOR%YELLOW}</action>{END}
	'''for action in scene.actions]) for scene in pb.scenes]))
	
	

		
