#!/usr/bin/python3

from functools import wraps

# This decorator class is intended to be used to associate certain methods to certain tags
# My Renderer implementations associate methods to tags regarding their names
class TagBinder:
	registry = {}	
	@classmethod
	def _append(this, cls_name, f_name, f):
		bindings = this.registry.get(cls_name, None)
		if bindings:
			bindings[f_name] = f
		else:
			this.registry[cls_name] = {f_name: f}
	@classmethod
	def bind(this, f):
		q = f.__qualname__
		cls_name, f_name = q.split('.')
		this._append(cls_name, f_name, f)
		return f
		
