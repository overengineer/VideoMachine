# VideoMachine

Generate videos from simple XML playbooks.
![](docs/hello.png)

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

