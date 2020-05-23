#!/usr/bin/python3

import os, sys, shutil, tempfile, time, subprocess, shlex, re
import logging
logger = logging.getLogger('lib')

class Voice:
	def __init__(self):
		self.temp_dir = tempfile.mkdtemp()
		
	def __del__(self):
		if self.temp_dir:
			shutil.rmtree(self.temp_dir)
		
	def say(self, txt):
		pass
		


class FliteVoice(Voice):
	def __init__(self, exec_path='flite', voice='rms', lang='en',
			duration_stretch: float = 0.9, int_f0_target_mean: int = 110):
		super().__init__()
		self.voice = voice
		self.d = duration_stretch
		self.f0 = int_f0_target_mean
		self.exec_path = exec_path
		
	def say(self, txt):
		_, path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir) 
		subprocess.call([self.exec_path, 
		"--setf", f"int_f0_target_mean={self.f0}",
		"--setf", f"duration_stretch={self.d}",
		"-voice", shlex.quote(self.voice),
		"-t", shlex.quote(txt),  
		"-o", shlex.quote(path)])
		return [path]
		

class EspeakNgVoice(Voice):
	def __init__(self, exec_path='espeak-ng', lang='en', 
			pitch: int = 50, speed: int = 175, k: int = 0):
		super().__init__()	
		self.lang = lang
		self.pitch = pitch
		self.speed = speed
		self.k = k
		self.exec_path = exec_path
		
	def say(self, txt):
		_, path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir) 
		subprocess.call([self.exec_path, 
		f"-v{self.lang}",
		f"-k{self.k}",
		f"-s{self.speed}",
		f"-p{self.pitch}", 
		shlex.quote(txt), 
		"-w", shlex.quote(path)])
		return [path]


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

class GttsVoice(Voice):
	def __init__(self, octaves=0, speed=1, lang='en-uk'):
		super().__init__()
		self.lang = lang
		self.octaves = octaves
		oct_str = str(octaves)
		if oct_str[0]!='-': 
			oct_str = '+'+oct_str
		self.oct_str = oct_str
		self.speed = speed

	def say(self, txt):
		import gtts
		#source_filename = f"{hash(txt)}-{self.lang}"
		#source_filepath = os.path.join(self.temp_dir, source_filename + ".mp3")
		i = 0	
		paths = []
		if len(txt)>100:
			parts = re.split(r'[\.!?:,]', txt)
			for s in combine_parts(parts):
				_, path = tempfile.mkstemp(suffix='.mp3', dir=self.temp_dir) 
				time.sleep(0.5)
				while True:
					try:
						voice = gtts.gTTS(s, lang=self.lang)
						break
					except:	
						i += 1		
						logger.info('Retry: ', i)
						time.sleep(1)
				voice.save(path)
				paths.append(path)
		else:
			_, path = tempfile.mkstemp(suffix='.mp3', dir=self.temp_dir) 
			voice = gtts.gTTS(txt, lang=self.lang)
			voice.save(path)
			paths.append(path)
		#sampled_filename = f"tmp_{source_filename}{self.oct_str}.wav"
		#sampled_filepath = os.path.join(self.temp_dir, sampled_filename)

		return paths #self.change_pitch(source_filepath)

	# BAD QUALITY PITCH SHIFT, NOT RECOMMENDED
	def change_pitch(self, source_filepath):
		import pydub
		from audiotsm.io.wav import WavReader, WavWriter
		from audiotsm import phasevocoder
		if abs(self.octaves) > 0.1:
			_, sampled_filepath = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir) 

			sound = pydub.AudioSegment.from_mp3(source_filepath)
			sample_rate = int(sound.frame_rate * (2**self.octaves))
			modified = sound._spawn(sound.raw_data, overrides={"frame_rate":sample_rate})

			modified.export(sampled_filepath, format="wav")
		else:
			sampled_filepath = source_filepath
		if abs(self.speed - 1) > 0.1:
			#output_filepath = f"{os.path.basename(source_filepath)}{self.oct_str}_{self.speed}.wav"
			_, output_filepath = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir) 
			with WavReader(sampled_filepath) as reader:
				with WavWriter(output_filepath, reader.channels, reader.samplerate) as writer:
					tsm = phasevocoder(reader.channels, 
					speed=self.speed*(sound.frame_rate/sample_rate))
					tsm.run(reader, writer)
			return output_filepath
		else:
			return sampled_filepath
