#!/usr/bin/python3
from moviepy.editor import (ImageClip, AudioFileClip, AudioClip, 
				CompositeVideoClip, concatenate_audioclips, concatenate_videoclips)
#import moviepy.video.fx.all as vfx

from snippets.snippet import Snippet
from voice.tts import *
from utils import *
from error_handling import handle_render_not_implemented_error, handle_node_error

import tempfile, re, time, os, shutil, itertools
import logging
logger = logging.getLogger('lib')

class Scene:
	clips = []
	def __init__(self, scene):
		self.scene = scene
		self.temp_dir = tempfile.mkdtemp()	
		self._render()
		
	def __del__(self):
		if self.temp_dir:
			shutil.rmtree(self.temp_dir)
		
	def _get_tag_method(self, name):
		assert re.match("^[a-z]+$", name), "Unsafe XML tag: "+name
		return self.__class__.__dict__[name]
	
	def _render(self):
		for node in self.scene.actions:
			try:
				logger.debug(node)
				self._get_tag_method(node.name)(self, node)
			except NotImplementedError:
				handle_render_not_implemented_error(self, node)
			except:
				msg = f'Rendering action "{node.name}" failed.'
				handle_node_error(node, msg)	


class CodingScene(Scene):
	clips = []
	sounds = []
	images = []
	hl_lines = []
	snippet = None
	background_image = 'assets/matrix.jpg'
	
	def __init__(self, scene):
		self.voice = scene.voice
		self.w = int(scene.w)
		self.h = int(scene.h)
		self._push_image(self.background_image)
		super().__init__(scene)
		if self.images or self.sounds:
			self._compose_buffer()
		
	def _push_snippet(self):
		_, img_path = tempfile.mkstemp(suffix='.png', dir=self.temp_dir)
		logger.debug(img_path)
		lines = self.snippet.text.split('\n')
		offset = 20
		font_size_h = (self.h-offset)/len(lines)
		font_size_w = (self.w-offset)/max([len(s) for s in lines])
		font_size = min(font_size_w, font_size_h) 
		font_size = min(font_size, 128)
		self.snippet.to_image(out_path=img_path, hl_lines=self.hl_lines, font_size=font_size)
		self._push_image(img_path)
		
	def _push_sound_file(self, path):
		sound = AudioFileClip(path)
		self.sounds.append(sound)
		
	def _push_image(self, image):
		clip = ImageClip(image).set_position('center')#.fx(vfx.resize, width=self.w)

		self.images.append(clip)
		
	def _compose_buffer(self):
		audio = concatenate_audioclips(self.sounds)
		assert self.images, self.scene.soup
		video = CompositeVideoClip(self.images, 
			size=(self.w, self.h)).set_duration(audio.duration)
		video = video.set_audio(audio)
		self.clips.append(video)
		self.sounds, self.images = [], []
		
	def _render(self):	
		super()._render()
		self._compose_buffer()
		
	def code(self, node):
		assert self.snippet == None, "code tag placed in the scene twice"
		text = deindent(node.decode_contents())
		self.snippet = Snippet(text, lang=node.attrs.get('lang',''))
		self._push_snippet()
				
	def hl(self, node):
		# lines Empty by default
		lines = [int(s) for s in node.attrs.get('lines', '').split()]
		if not lines:
			if lines := self.hl_lines: # Dont change if empty
				lines = [int(lines[0])+1] # Next line
		# Update Snippet
		if self.hl_lines != lines:
			self._compose_buffer()
			self.hl_lines = lines
			self._push_snippet()
		# tts & reset hl
		self.tts(node)
		if not node.isSelfClosing:
			self.hl_lines = []
		
	def tts(self, node):
		voice = self.voice
		if voice_attr := node.attrs.pop('class', None):
			if voice_class := globals().get(voice_attr, None):
				voice = voice_class(**node.attrs)
		if txt := node.decode_contents().strip():
			paths = voice.say(txt)
			for path in paths:
				self._push_sound_file(path)
				logger.debug(path)
		if node.isSelfClosing:
			self.voice = voice
				
	def wait(self, node):
		silence = AudioClip(lambda t: (0,0), 
			duration=float(node.attrs.get('sec', 0.5))).set_start(0)
		self.sounds.append(silence)


def render_playbook(pb):
	clips = []
	import json
	#print(json.dumps([[str(action)for action in scene.actions] for scene in pb.scenes],indent=4))
	
	for scene in pb.scenes:
		print(scene.soup)
		print(scene.actions)
		render = globals()[scene.class_name](scene=scene)
		print(render.clips)
		print('========================================')
		clips += render.clips
	print(clips)
	clip = concatenate_videoclips(clips)
	return clips[0]
		
	
