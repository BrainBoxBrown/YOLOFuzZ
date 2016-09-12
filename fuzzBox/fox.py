import re
import os
import sys
import json
import time
import uuid
import gdb
from functools import partial

# should probably add something
# to a config file to select what module to run
from binMods import *

peda = {}
run_id = ""
# print peda
# this is the FuzzBox (fox)
# it will run a transcript through gdb 

# load all the jmp flipping stuff here
# make it nice and modular
gdb_run = partial(gdb.execute, to_string=True)
config_file = os.getcwd() + "/../config.json"
my_config = {}
with open(config_file, "r") as f:
	my_config = json.loads(''.join(f.readlines()))


def dump(obj):
  for attr in dir(obj):
	print "obj.%s = %s" % (attr, str(getattr(obj, attr)))

def get_saved_eip():
	try:
		response = gdb_run("info frame")
		p = re.compile(r'saved .ip\s*=\s*(0x[a-f0-9]+)')
		matches = p.findall(response)
		saved_eip = None
		if len(matches) == 1:
			saved_eip = matches[0]
		return saved_eip
	except:
		return None

def exit_handler(event):
	"""
		here we will handle a crash and produce a report
	"""
	global run_id
	print "event type: exit"
	with open("../reports/"+ my_config["prog_name"] + "/" + run_id, "a") as report:
	# save the program output to the crash report
		with open("./output.txt", "r") as output:
			report.write("Program Output:\n" + '\n'.join(output.readlines()))
	os.remove("output.txt") # cleanup
	
def stop_handler(event):
	# todo: ask the mod if it has anything to do with this
	if "breakpoint" in dir(event):
		print "This shouldn't happen"
		gdb_run("c")
		return

	global run_id
	print "event type: stop"
	with open("../reports/"+ my_config["prog_name"] + "/crash-" + run_id, "w") as report:

		# do a crashdump
		report.write(gdb_run("crashdump " + event.stop_signal))

		report.write("makde it")
		# get the return address
		saved_eip = get_saved_eip()
		if saved_eip == None:
			return
		# if saved_eip != None:
		report.write("saved return address:" + saved_eip + "\n")
		# if the saved eip/rip is not valid
		if not peda.is_address(int(saved_eip, 16)):
			report.write("saved return address is not valid, hmmm :)\n")


# this is going to be useful :)
# profile 0 jmp


def execute(num, _peda):
	"""
		Execute <num> many fuzzes
	"""
	global peda
	global run_id

	peda = _peda
	# print peda
	binaryModder = JmpFlip(peda)

	# make a directory to put the crash reports
	directory = "../reports/"+my_config["prog_name"]+"/"
	if not os.path.exists(directory):
		os.makedirs(directory)


	# gdb_run("catch signal SIGSEGV")
	# gdb_run("catch signal SIGABRT")

	for x in range(num):
		run_id = str(uuid.uuid4())
		gdb_run("start {args} < ../Transcript.txt > output.txt".format(args=my_config["args"]))
		cmds = binaryModder.prep()
		with open("../reports/"+ my_config["prog_name"] + "/" + run_id, "w") as report:
			report.write("Commands run:\n" + cmds)
		gdb.events.exited.connect(exit_handler)
		gdb.events.stop.connect(stop_handler)
		gdb_run("c")
		gdb.events.exited.disconnect(exit_handler)
		gdb.events.stop.disconnect(stop_handler)









