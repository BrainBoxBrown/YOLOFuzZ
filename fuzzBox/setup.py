#!/usr/bin/python
import os
import sys
import json
# import gdb
# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(os.getcwd() + "/.."))



config_file = os.getcwd() + "/../config.json"
config = {}
with open(config_file, "r") as f:
	config = json.loads(''.join(f.readlines()))
config["prog"] = os.getcwd() + "/../tests/simple"
config["prog_path"] = os.getcwd() + "/../tests/"
config["prog_name"] = "simple"

with open(config_file, "w") as f:
	f.write(json.dumps(config))

# Do the import
# import fox.py
import fuzzBox

# I should make some class here and put
# peda in that .. hmm

fuzzBox.fox.execute(0, peda)