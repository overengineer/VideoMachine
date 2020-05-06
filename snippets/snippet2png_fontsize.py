#!/usr/bin/python3

from snippet import Snippet
from utils import *
		
text = """

#!/usr/bin python3

print('hello world!')

"""

with open('example.html') as fp:
	text = fp.read().strip()
text = text[:int(len(text)/32)]


snippet = Snippet(text)
png_path = 'hello.png' 

screen_width_px, screen_height_px = 1920, 1080
font_size_px = 16
snippet.to_image(png_path, font_size = font_size_px)

size = [1920, 1080]
scale_image(png_path, 'scaled.png', size)




