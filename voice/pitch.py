#!/usr/bin/python3

import os, sys, tempfile, gtts

def abbr(s):
	import re
	words = str(re.sub(r'[^a-z ]','',s.lower())).split()
	with open("../nlp/stop.txt") as f:
		stop = f.read().lower().split("\n")
	words = [w.strip()[:4] for w in words if w not in stop][:4]
	return '_'.join(words)
	
try:
	octaves = float(sys.argv[1])
	speed = float(sys.argv[2])
	assert speed > 0
	lang = sys.argv[3]
	txt = sys.argv[4]
except:
	print(55*"="+"\nUsage: python3 pitch.py <octaves> <speed> <lang> <text>\n"+"="*55)
	sys.exit(-1)

temp_dir = tempfile.mkdtemp()	
source_filename = f"{abbr(txt)}-{lang}"
source_filepath = os.path.join(temp_dir, source_filename + ".mp3")

voice = gtts.gTTS(txt, lang=lang)
voice.save(source_filepath)


if abs(octaves) > 0.1:
	import pydub
	sound = pydub.AudioSegment.from_mp3(source_filepath)
	sample_rate = int(sound.frame_rate * (2**octaves))
	modified = sound._spawn(sound.raw_data, overrides={"frame_rate":sample_rate})

	oct_str = str(octaves)
	if oct_str[0]!='-': 
		oct_str = '+'+oct_str
	sampled_filename = f"tmp_{source_filename}{oct_str}.wav"
	sampled_filepath = os.path.join(temp_dir, sampled_filename)
	modified.export(sampled_filepath, format="wav")
	
	from audiotsm import phasevocoder
	from audiotsm.io.wav import WavReader, WavWriter

	output_filepath = f"{os.path.basename(source_filename)}{oct_str}_{speed}.wav"
	with WavReader(sampled_filepath) as reader:
		with WavWriter(output_filepath, reader.channels, reader.samplerate) as writer:
		    tsm = phasevocoder(reader.channels, speed=speed*(sound.frame_rate/sample_rate))
		    tsm.run(reader, writer)
