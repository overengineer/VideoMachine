#!/usr/bin/python3

import os, sys, tempfile, time, gtts
import pydub
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter


class Voice:
	def __init__(self, octaves, speed=1, lang='en', temp_dir=None):
		self.lang = lang
		self.octaves = octaves
		oct_str = str(octaves)
		if oct_str[0]!='-': 
			oct_str = '+'+oct_str
		self.oct_str = oct_str
		self.speed = speed
		if not temp_dir:
			temp_dir = tempfile.mkdtemp()	
		self.temp_dir = temp_dir

	def say(self, txt):
		assert len(txt)<=100, "Too long text"
		#source_filename = f"{hash(txt)}-{self.lang}"
		#source_filepath = os.path.join(self.temp_dir, source_filename + ".mp3")
		_, source_filepath = tempfile.mkstemp(suffix='.mp3', dir=self.temp_dir) 
		i = 0	
		while True:
			try:
				voice = gtts.gTTS(txt)
				break
			except:	
				i += 1		
				print('Retry: ', i)
				time.sleep(1)
		voice.save(source_filepath)
		#sampled_filename = f"tmp_{source_filename}{self.oct_str}.wav"
		#sampled_filepath = os.path.join(self.temp_dir, sampled_filename)

		return self.change_pitch(source_filepath)


	def change_pitch(self, source_filepath):
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
