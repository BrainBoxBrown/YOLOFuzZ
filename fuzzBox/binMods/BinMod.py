#!/usr/bin/python
import os
import json
class BinMod( object ):
	"""
		a BinMod fucks shit up using gdb
	"""

	def __init__(self, _peda):
		"""
			Setup gdb how we like it
		"""

		# load the config file and save it as a variable
		config_file = os.getcwd() + "/../config.json"
		config = {}
		with open(config_file, "r") as f:
			config = json.loads(''.join(f.readlines()))

		self.config = config
		self.peda = _peda

	def update(self):
		"""
			make some tweaks
		"""