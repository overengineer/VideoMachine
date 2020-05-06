#!/usr/bin/python3

import os.path
svg_path = os.path.realpath("termtosvg_xmplv3ek/termtosvg_00217.svg")
print(svg_path)

"""
import wand.image
with open("termtosvg_xmplv3ek/termtosvg_00161.svg","rb") as svg_file:
	image=wand.image.Image(blob=svg_file.read(), format="svg")
	with open("wand.png","wb") as png_file:
		png_file.write(image.make_blob("png"))
	

from cairosvg import svg2png
with open("termtosvg_xmplv3ek/termtosvg_00161.svg","r") as svg_file:
	svg2png(bytestring=svg_file.read(), write_to='svg2png.png')
	
	
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
drawing = svg2rlg(svg_path)
renderPM.drawToFile(drawing, "reportlab.png", fmt="PNG")
	
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = True
driver = webdriver.Firefox("tmp", options=options)	

driver.get("file://"+svg_path)
driver.get_screenshot_as_file("firefox.png")
driver.close()
