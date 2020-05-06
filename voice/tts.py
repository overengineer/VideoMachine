#!/usr/bin/python3

import os, sys, tempfile, gtts
import pydub
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter


class Voice:
	def __init__(octaves, speed=1, temp_dir=None):
		self.octaves = octaves
		oct_str = str(octaves)
		if oct_str[0]!='-': 
			oct_str = '+'+oct_str
		self.oct_str = oct_str
		self.speed = speed
		if not temp_dir:
			temp_dir = tempfile.mkdtemp()	
		self.temp_dir = temp_dir

	def say(self, text):
		source_filename = f"{hash(txt)}-{lang}"
		source_filepath = os.path.join(self.temp_dir, source_filename + ".mp3")
		
		voice = gtts.gTTS(txt, lang=lang)
		voice.save(source_filepath)
		sampled_filename = f"tmp_{source_filename}{self.oct_str}.wav"
		sampled_filepath = os.path.join(self.temp_dir, sampled_filename)
		change_pitch(source_filepath, sampled_filepath)
		return sampled_filepath


	def change_pitch(self, source_filepath, sampled_filepath):

		sound = pydub.AudioSegment.from_mp3(source_filepath)
		sample_rate = int(sound.frame_rate * (2**self.octaves))
		modified = sound._spawn(sound.raw_data, overrides={"frame_rate":sample_rate})

		modified.export(sampled_filepath, format="wav")

		output_filepath = f"{os.path.basename(source_filename)}{self.oct_str}_{self.speed}.wav"
		with WavReader(sampled_filepath) as reader:
			with WavWriter(output_filepath, reader.channels, reader.samplerate) as writer:
				tsm = phasevocoder(reader.channels, 
				speed=self.speed*(sound.frame_rate/sample_rate))
				tsm.run(reader, writer)
