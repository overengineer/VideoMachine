#!/usr/bin/python3

from collections import OrderedDict
						
def count_prefix(line, prefix):
	for i, c in enumerate(line):
		if c != prefix:
			return i
	return i
	
def remove_prefix(line, prefix, n=1):
	for i, c in enumerate(line):
		if i==n or c != prefix:
			return line[i:]
	return line[i:]

def deindent(text):
	lines = [line for line in text.split('\n') if line.strip()]
	n = count_prefix(lines[0],'\t')
	lines = [remove_prefix(line, '\t', n) for line in lines]
	text = '\n'.join(lines)
	return text

