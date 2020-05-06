#!/usr/bin/python3

def get_temp_dir(path=''):
	import os.path
	temp_dir = os.path.realpath(path)
	if not os.path.exists(temp_dir):	
		os.mkdir(temp_dir)	
	return temp_dir

def scale_image(src_path, dst_path, size, fmt="PNG"):
	from PIL import Image
	im = Image.open(src_path)
	if im.size[0] < size[0] and im.size[1] < size[1]:
		print("WARNING: Image is scaled up. Result will be noisy.")
	aspect_ratio = im.size[0] / im.size[1]
	if size[0]/size[1] < aspect_ratio:
		size[1] = int(size[0]/aspect_ratio)
	else:
		size[0] = int(size[1]*aspect_ratio)
	# Resize:
	scaled = im.resize(size, Image.BICUBIC)
	scaled.save(dst_path, fmt)
	
