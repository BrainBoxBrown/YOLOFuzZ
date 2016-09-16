import re
import os
import sys
import json
import time
import uuid
import gdb
import datetime
from functools import partial

# should probably add something
# to a config file to select what module to run
from binMods import *

peda = {}
run_id = ""
# this is the FuzzBox (fox)
# it will run a transcript through gdb 

# load all the jmp flipping stuff here
# make it nice and modular
gdb_run = partial(gdb.execute, to_string=True)
config_file = os.getcwd() + "/../config.json"
my_config = {}
with open(config_file, "r") as f:
	my_config = json.loads(''.join(f.readlines()))

report_file = "./banana"
def dump(obj):
  for attr in dir(obj):
	print "obj.%s = %s" % (attr, str(getattr(obj, attr)))

def get_saved_eip(): 
	#  Frame.read_register try this instead
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
	global gdb_run
	global report_file
	print "event type: exit"
	with open(report_file, "a") as report:
		# save the program output to the crash report
		with open("./output.txt", "r") as output:
			report.write("\nProgram Output:\n" + '\n'.join(output.readlines()))
	os.remove("output.txt") # cleanup
	
def stop_handler(event):
	global gdb_run
	# todo: ask the mod if it has anything to do with this
	print "hladfsjklhdasfhjkladsfklhjadfslkjkldfjs"
	if "breakpoint" in dir(event):
		print "This shouldn't happen"
		print gdb_run("c")
		return

	global report_file
	print "event type: stop"
	print report_file
	with open(report_file, "a") as report:

		# do a crashdump
		dmp = gdb_run("crashdump ")# + event.stop_signal)
		report.write(dmp)
		print dmp

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
	global gdb_run
	global report_file
	report_folder = my_config["report_dir"] + my_config["prog_name"] 
	peda = _peda
	gdb_run = peda.execute_redirect
	gdb_run("file " + my_config["prog_path"] + my_config["prog_name"])
	# gdb_run("set startup-with-shell on")
	# _peda.execute("set interactive-mode on")
	# gdb_run("set verbose on")


	gdb_run(
		"set args {args} < {transcript_file} > output.txt".format(
			args=my_config["args"],
			transcript_file=my_config["transcript"]
		)
	)

	binaryModder = JmpFlip(peda, report_folder)

	try:
		# make a directory to put the crash reports
		directory = my_config["report_dir"]+my_config["prog_name"]+"/"
		if not os.path.exists(directory):
			os.makedirs(directory)
	except:
		pass

	# gdb_run("catch signal SIGSEGV")
	# gdb_run("catch signal SIGABRT")
	report_detail = "Arguments: {args}\nTranscript file: {transcript_file}\n".format(
		args=my_config["args"],
		transcript_file=my_config["transcript"]
	)


	for x in range(num):
		try:
			report_file_base = report_folder + "/{:%Y-%m-%d-%H-%M-%S}".format(datetime.datetime.now())
			run_id = str(uuid.uuid4())
			report_file = report_file_base + run_id
			binaryModder.prep(report_file) # enables all the breakpoints
			binaryModder.report(report_detail)
			binaryModder.report("PrepJmps:")
			print gdb_run("start")
			binaryModder.fuzz()
			binaryModder.report("MainJmps:")
			gdb.events.exited.connect(exit_handler)
			gdb.events.stop.connect(stop_handler)
			print gdb_run("c") # need timeout
			gdb.events.exited.disconnect(exit_handler)
			gdb.events.stop.disconnect(stop_handler)
			binaryModder.flush_report()
		except:
			pass









