#!/usr/bin/python3
import os, tempfile 

class Snippet:
	def __init__(self, text, lexer=None, style=None):
		self.text = text
		if lexer == None:
			from pygments.lexers import guess_lexer
			lexer = guess_lexer(text)
		self.lexer = lexer
		if style == None:
			from .solarized import SolarizedStyle
			style = SolarizedStyle
		self.style = style
		
	def to_image(self, out_path=None, style=None, fmt='PNG', **kwargs):
		from pygments import highlight
		from pygments.formatters import ImageFormatter
		if style == None:
			style = self.style
		formatter = ImageFormatter(format=fmt, style=style, **kwargs)
		return highlight(self.text, self.lexer, formatter, out_path)
		
	def to_html(self, out_path=None, style=None, **kwargs):
		from pygments import highlight
		from pygments.formatters import HtmlFormatter
		if style == None:
			style = self.style
		formatter = HtmlFormatter(style=style, full=True, **kwargs)
		html = highlight(self.text, self.lexer, formatter)
		if out_path:
			with open(out_path, "w") as fp:
				fp.write(html)
		return html
		
	def __repr__(self):
		return f'Snippet("{self.__str__()}")'
	
	def __str__(self):
		return self.text
