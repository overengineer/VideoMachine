# VideoMachine

Generate videos from simple XML playbooks.
![<?xml version="1.0" encoding="utf-8"?>
<playbook class="CodingScene" voice="GttsVoice" lang="en">
<scene>
	<code>
	#!/usr/bin/python3
	print('Hello World!')
	exit()
	</code>
	Hi guys. Today I'm gonna show you how to write a simple program in Python.
	
	<wait sec="0.5"/>
	
	<hl lines="1">
	The first line is a special comment that, indicates which executable to be used, to run this file.
	</hl>

	<wait sec="0.5"/>
	<hl lines="2">
	In the second line, we are calling a function named print, which writes a message to the standart output stream.
	</hl>

	<wait sec="0.5"/>
</scene>](docs/hello.png)

This project uses moviepy module. This is a work in progress. Intended to be an extensible library/framework-like thing. 
Now only generates silly TTS coding tutorials.


## Installation

Clone this repo. Not added `setup.py` yet

## Usage

```
python3 main.py path/to/playbook.xml
```

## Extending

Extend `render.Scene` class for new types of Scenes. 
New tag handler method names should match corresponding tag name.

New voice subclasses should inherit `voice.tts.Voice` class and should implement `say(self, txt)` method.

