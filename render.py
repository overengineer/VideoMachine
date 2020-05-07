#!/usr/bin/python3
from snippets.snippet import Snippet
from moviepy.editor import (ImageClip, AudioFileClip, AudioClip, 
				CompositeVideoClip, concatenate_audioclips, concatenate_videoclips)
from voice.tts import *
from error_handling import handle_render_not_implemented_error, handle_node_error
import tempfile, re, time, os, sys

# TODO: carry this mechanism to Voice class
def combine_parts(parts, n=100):
	parts.reverse()
	while True:
		if not parts:	
			break
		p = parts.pop().strip() 
		if not parts:
			if p:	
				yield p
			break
		q = parts.pop().strip() 
		if len(p)+len(q) <= 100:
			p = p + ', ' + q
			parts.append(p)
		elif p:
			yield p
			parts.append(q)

class SceneRender:
	def __init__(self, scene):
		self.scene = scene
		self._render()
	
	def _render(self):
		for node in self.scene.actions:
			try:
				print(node)
				self.__class__.__dict__[node.name](self, node)
			except NotImplementedError:
				handle_render_not_implemented_error(self, node)
			except:
				msg = f'Rendering action "{node.name}" failed.'
				handle_node_error(node, msg)
				

# Inherit from SceneRenderer class
class CodingSceneRender(SceneRender):
	clips = []
	sounds = []
	images = []
	hl_lines = []
	snippet = None
	
	def __init__(self, *args, voice=None, temp_dir=None, **kwargs):
		self.voice = voice or FliteVoice()#-0.28, speed=1.15)
		if not temp_dir:
			temp_dir = tempfile.mkdtemp()	
		self.temp_dir = temp_dir
		super().__init__(*args, **kwargs)
		
	def code(self, node):
		assert self.snippet == None, "code tag placed in the scene twice"
		text = str(node.string)
		self.snippet = Snippet(text)
		self._push_snippet()
		
	def _push_snippet(self):
		_, img_path = tempfile.mkstemp(suffix='.png', dir=self.temp_dir)
		print(img_path)
		self.snippet.to_image(out_path=img_path, hl_lines=self.hl_lines)
		self._push_image(img_path)
		
	def _push_sound_file(self, path):
		sound = AudioFileClip(path)
		self.sounds.append(sound)
		
	def _push_image(self, image):
		clip = ImageClip(image)
		self.images.append(clip)
		
	def _compose_buffer(self):
		audio = concatenate_audioclips(self.sounds)
		video = CompositeVideoClip(self.images).set_duration(audio.duration)
		video = video.set_audio(audio)
		self.clips.append(video)
		self.sounds, self.images = [], []

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
			# TODO: FIX THIS LINE
			if self.voice.__class__.__name__=='GttsVoice' and len(txt)>100:
				parts = re.split(r'[\.!?:,]', txt)
				for s in combine_parts(parts):
					time.sleep(0.5)
					path = self.voice.say(s)
					self._push_sound_file(path)
					print(path)
			else:
				path = self.voice.say(txt)
				self._push_sound_file(path)
				print(path)
				
	def wait(self, node):
		silence = AudioClip(lambda t: (0,0), duration=float(node.attrs['sec'])).set_start(0)
		self.sounds.append(silence)
		
	def _render(self):	
		super()._render()
		self._compose_buffer()
		
# PLAYBOOK RENDER CLASS
			
if __name__=='__main__':
	from datetime import datetime
	from parse import Playbook
	STRICT = False

	def echo(s):
		RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(31,38)
		END = "\033[0m"
		COLOR = "\033[1;%dm"
		print(f"""{COLOR%GREEN}{datetime.now().strftime('%H:%M:%S')}{END} {COLOR%MAGENTA}{s}{END}
		""")
	echo("PARSING")
	pb_path = sys.argv[1]
	pb = Playbook(pb_path)
	echo("RENDERING")

	render = CodingSceneRender(pb.scenes[0])
	echo("COMPOSING")
	print(render.clips)
	final_video = concatenate_videoclips(render.clips)
	echo("WRITING")
	final_video.write_videofile(os.path.basename(pb_path)+".mp4", fps=30)
	echo("FINISH")
	
		
