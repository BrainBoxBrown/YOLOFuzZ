#!/usr/bin/python
import os
import json
import gdb
from functools import partial
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
		my_config = {}
		with open(config_file, "r") as f:
			my_config = json.loads(''.join(f.readlines()))

		self.my_config = my_config
		self.peda = _peda
		self.gdb_run = partial(gdb.execute, to_string=True)
		self.gdb_run("file " + self.my_config["prog_path"] + self.my_config["prog_name"])

	# def prep(self):

	# def update(self):
	# 	"""
	# 		make some tweaks
	# 	"""