#!/usr/bin/python3

from snippet import Snippet
from utils import *
		
text = """

#!/usr/bin python3

print('hello world!')

"""
"""
with open('example.html') as fp:
	text = fp.read().strip()

text = text[:int(len(text)/32)]
"""
snippet = Snippet(text)

import os
	
			
png_path = os.path.join(temp_dir, "hello2.png")
html_path = os.path.join(temp_dir, "hello2.html")

html = snippet.to_html(hl_lines=[1])
"""
import lxml.html
from lxml.etree import tostring

page = lxml.html.fromstring(html)
new_style = lxml.html.Element('style')
new_style.text = '''
pre { font-size: 32px; }
'''
page.xpath('//style')[0].addnext(new_style)
"""

with open(html_path, "w") as fp:
	fp.write(html) #tostring(page).decode('utf-8'))
# import sys
# sys.exit(0)

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = False
browser = webdriver.Firefox("tmp", options=options)	
browser.get("file://"+html_path)

screen_width_px, screen_height_px = 1920, 1080
browser.set_window_size(screen_width_px, screen_height_px)
lines = snippet.text.split('\n')
row_height_ch = len(lines)
row_height_px = screen_height_px / row_height_ch
row_width_ch = max([len(line) for line in lines])

line_height_px = 1.75 * screen_width_px / row_width_ch
line_height_px = 1.75 * (screen_width_px - line_height_px) / row_width_ch
if row_height_ch * line_height_px / 0.75 > screen_height_px - line_height_px:
	print(line_height_px)
	line_height_px = 0.75 * (screen_height_px - line_height_px) / (row_height_ch + 1)
	print(line_height_px)
font_size_px = line_height_px

browser.execute_script("""
var style = document.createElement('style');
style.innerHTML = `
  pre { 
    font-family: "Lucida Console";
    font-size: %(font-size)spx;
    line-height: %(line-height)spx;
  }
`;
document.head.appendChild(style);
""" % {'font-size':font_size_px, 'line-height':line_height_px})
browser.get_screenshot_as_file("firefox.png")
browser.close()

import sys
sys.exit(0)

from moviepy.video.VideoClip import ImageClip
clip = ImageClip(png_path).set_position(("center","top")).set_duration(4.0)
clip.write_videofile("hello2.mp4", fps=60, codec="libx264")
clip.close()


