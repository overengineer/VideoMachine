# VideoMachine

Generate videos from simple XML playbooks.
```xml
<?xml version="1.0" encoding="utf-8"?>
<playbook class_name="CodingScene" w="1920" h="1080">
<scene>
	<code>
	#!/usr/bin/python3
	print('Hello World!')
	</code>
	<tts>
	This line prints "Hello World!" to console.
	</tts>
	<wait sec="0.5"/>
</scene>
```

This project uses moviepy module. This is a work in progress. Intended to be an extensible library/framework-like thing. 
Now only generates silly TTS coding tutorials.
Example output: https://youtu.be/VKi5sNB40yA

##  Status

In Progress


## Installation

```
git clone https://github.com/overengineer/VideoMachine.git
cd VideoMachine
pip3 install -r requirements.txt
```

## Dependencies

You should have installed one of TTS tools below to generate TTS tracks. 
- flite
- espeak-ng
- gTTS

Alternatively, you can write TTS wrapper for other TTS engines/APIs. See [extending](#extending).

## Usage

```
python3 main.py path/to/playbook.xml
```

## Playbook Syntax

`playbook`s consist of scenes. `scene`s contains actions (e.g. `<code>` tag for code snippets). 
tags may have attributes. This attributes override some default settings.

### Playbook Attributes

`class_name` : it globally sets default `class_name` for `scene` instances. (e.g. `CodingScene`)
`w`, `h`: width & height of the canvas

### `CodingScene` class

This class is the build-in example sub-class of the `Scene` class.
It can be used to render coding tutorials.

#### `CodingScene`: supported action tags & their attributes

- `code`: Renders syntax highlighted code snippets using Pygments.
	- `lang`: Programming language. ("python", "java" etc.)
	- `escape`: Allow HTML escape sequences. (set "true" when `<![CDATA` used.) 
- `tts`: Generates text-to-speech. Self closing tags overrides default voice.
	- `voice`: Name of TTS class. Look [voice/tts.py](voice/tts.py)
	- `lang`: Language of the text.
	- ... : Each TTS class have their own special attributes.
- `wait`: insert silence for the given seconds. (or default). This tag should be self closing.

## Extending

Extend `render.Scene` class for new types of Scenes. 
New tag handler method names should match corresponding tag name.

New voice subclasses should inherit `voice.tts.Voice` class and should implement `say(self, txt)` method.

