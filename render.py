#!/usr/bin/python3
from moviepy.editor import (ImageClip, AudioFileClip, AudioClip, 
				CompositeVideoClip, concatenate_audioclips, concatenate_videoclips)
#import moviepy.video.fx.all as vfx

from snippets.snippet import Snippet
from voice.tts import *
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
	
	def __init__(self, scene):
		self.voice = scene.voice
		self.w = int(scene.w)
		self.h = int(scene.h)
		super().__init__(scene)
		
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
		text = str(node.string)
		self.snippet = Snippet(text, lang=node.attrs.get('lang',''))
		self._push_snippet()
				
	def hl(self, node):
		lines = [int(s) for s in node.attrs.get('lines', '').split()]
		# Update Snippet
		if self.hl_lines != lines:
			self._compose_buffer()
			self.hl_lines = lines
			self._push_snippet()
		# tts & reset hl
		if not node.isSelfClosing:
			self.tts(node)
			self.hl_lines = []
		
	def tts(self, node):
		txt = str(node.string).strip()
		if txt:
			paths = self.voice.say(txt)
			for path in paths:
				self._push_sound_file(path)
				logger.debug(path)
				
	def wait(self, node):
		silence = AudioClip(lambda t: (0,0), duration=float(node.attrs['sec'])).set_start(0)
		self.sounds.append(silence)

		
def render_playbook(pb):
	clips = []
	for scene in pb.scenes:
		# TODO: scene subclasses
		render = globals()[scene.class_name](scene=scene)
		logger.debug(render.clips)
		clips.append(render.clips)
	# flatten list
	clips = list(itertools.chain.from_iterable(clips))
	clip = concatenate_videoclips(clips)
	return clip
		
	
