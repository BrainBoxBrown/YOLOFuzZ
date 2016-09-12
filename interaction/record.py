#!/usr/bin/env python3

#
# The purpose of this program is to 
# get the user to run the program
# and we then record their interaction
# and put it in a repeatable format
# for the replay module
# 
# - pasteBin
from subprocess import *

def get_prog_name():
	"""
		Get the program to run
		TODO:
		autocompled like shell 
		such friendly
	"""
	prog_name = input("program name >")
	return prog_name


def get_args(prog_name):
	print("add any command line arguments")
	args = input(prog_name + " ")
	return args

# prog_name = get_prog_name()
# args = get_args(prog_name)
import subprocess
proc = subprocess.Popen(["../tests/simpleMACHO", "args"], stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
outs, errs = proc.communicate(input=bytes("8", "UTF-8"))
print(outs)
# something along those lines I thinnk
# with Popen(["ifconfig"], stdout=PIPE) as proc:
#     log.write(proc.stdout.read())

# call(["../tests/simpleMACHO", "args"])
# p = Popen(,stdin=PIPE)

# output = Popen(["../tests/simpleMACHO", "args"], stdin=PIPE, stdout=PIPE).communicate()[0]

# from subprocess import Popen, PIPE
# from threading import Thread

# start commands in parallel
# first = Popen("cat", stdout=PIPE)
# second = Popen(["../tests/simpleMACHO", "args"], stdin=first.stdout)
# first.stdout.close() # notify `first` if `second` exits 
# first.stdout = None # avoid I/O on it in `.communicate()`

# feed input to the first command
# print(first.communicate())
# Thread(target=first.communicate, args=[bytes("simple", 'UTF-8')]).start() # avoid blocking

# get output from the second command at the same time
# output = first.communicate()[0]

# from subprocess import Popen, PIPE
# p1 = Popen(["cat"], stdout=PIPE, stdin=PIPE)
# p1.communicate("8")
# print(output)

# ages later


# have some way of sending this to fuzbox
user_input = "8"

# need some other way to get the prog name and args
with open("./Transcript.txt", "w") as t:
	t.write(user_input)




















