#!/usr/bin/python3
import sys, traceback, logging
logger = logging.getLogger('lib')

RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(31,38)
END = "\033[0m"
COLOR = "\033[1;%dm"

STRICT = False

def handle_error(msg):
	if globals().get('STRICT', False):
		logger.error(msg)
		sys.exit(-1)
	else:
		logger.warning(msg)
		
def handle_node_error(node, message):
	msg = f'''\n{message}
	{COLOR%YELLOW}{node}{END}
	{COLOR%RED}{traceback.format_exc()}{END}'''
	handle_error(msg)
	
def handle_parsing_error(parser, node):	
	msg = f'Parsing "{node.name}" in "{parser.soup.name}" failed'
	handle_node_error(node, msg)
		
def handle_render_not_implemented_error(renderer, node):	
	msg = f'''Rendering "{node.name}" in "{renderer.soup.name}" failed.
	This tag is not associated with a render method.'''
	handle_node_error(node, msg)

