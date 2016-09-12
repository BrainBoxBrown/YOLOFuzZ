#!/usr/bin/python
import os
import sys
import json
# import gdb
# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(os.getcwd() + "/.."))



config_file = os.getcwd() + "/../config.json"
my_config = {}
with open(config_file, "r") as f:
	my_config = json.loads(''.join(f.readlines()))
my_config["prog"] = os.getcwd() + "/../tests/simpleMACHO"
my_config["prog_path"] = os.getcwd() + "/../tests/"
my_config["prog_name"] = "simpleMACHO"

with open(config_file, "w") as f:
	f.write(json.dumps(my_config))

# Do the import
# import fox.py
import fuzzBox

# I should make some class here and put
# peda in that .. hmm

fuzzBox.fox.execute(10, peda)