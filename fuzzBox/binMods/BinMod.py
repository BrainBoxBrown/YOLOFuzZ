#!/usr/bin/python
import os
import sys
import gdb
import json
from functools import partial

class FuzzBreakpoint (gdb.Breakpoint):
	"""
		Stop. Collaborate. Listen
		stop on a jmp and tell me if we 
		take the jump or not
	"""
	def __init__(self, break_data, _peda):
		"""
			blindly assign attributes based on a dictionary 
			passed in
		"""
		if "address" not in break_data:
			raise "You need to have 'address' in the initilisation data for a FuzzBreakpoint"
		self.valid = 0
		for key in break_data:
			setattr(self, key, break_data[key])
		self.peda = _peda
		self.report_file = ""
		self.gdb_run = _peda.execute_redirect

		super(FuzzBreakpoint, self).__init__("*"+self.address, gdb.BP_BREAKPOINT)

	def report_to_file(self, _report_file):
		self.report_file = _report_file

	def dump(self):
		return self.__dict__

	def stop (self):
		return False

	def report(self, msg):
		if self.report_file != "":
			with open(self.report_file, 'a') as f:
				f.write(msg + '\n')
		else:
			print 'fuck you'


class BinMod( object ):
	"""
		a BinMod fucks shit up using gdb

		to make a subclass you just need to override 
		the extract_breaks() function

	"""

	def __init__(self, _peda, _report_folder):
		"""
			Setup gdb how we like it
		"""
		# load the config file and save it as a variable
		self.report_folder = _report_folder
		self.peda = _peda
		self.run_count = -1 # so that it's 0 on first run
		self.gdb_run = _peda.execute_redirect
		self.report_buffer = ""
		self.fucked = False # start the day with a smile

		self.load_config()
		
		gdb.events.exited.connect(self.exit_handler)
		gdb.events.stop.connect(self.stop_handler)
		self.get_breaks()
		self.enable_breakp_range()# enables all valid breaks
		# if self.fucked_run():
		# 	print "whelp that didn't work ... :("
		# else:
		# 	print "y.ay 4 us. dat wrkd :)"
		gdb.events.exited.disconnect(self.exit_handler)
		gdb.events.stop.disconnect(self.stop_handler)

	def load_config(self):		
		config_file = os.getcwd() + "/../config.json"
		my_config = {}
		with open(config_file, "r") as f:
			my_config = json.loads(''.join(f.readlines()))
		self.my_config = my_config
		return
						
	def exit_handler(self, event):
		"""
			here we will handle a crash and produce a report
		"""
		return

	def stop_handler(self, event):
		self.fucked = True
		return

	def extract_breaks(self):
		"""
			This should be overriden
			return a list of breakpoint datas
			must have 'address'
		"""
		#self.breaks = the breakpoints we wnat
		return []

	def enable_breakp_range(self,low=0,high=-1,active=True):
		if high == -1:
			high = len(self.breaks)
		for breakp in self.breaks[low:high]:
			if active == False or breakp.valid != -1: # u no activate bad break!
				breakp.enabled = active



	def smart_search(self, low, high, will_fail=False):
		"""
			Binary search
			return true if no crash
			used for setting up breakpoints

			Does this smart thing where if a range 0 -> 10 crashes
			but then 0 -> 5 doesn't crash 
			it knows that 5 -> 10 will crash and that 5 -> 7 will
			be tested next
			this is useful becasue enabling and disabling 
			breakpoints is slow 
		"""
		for j in self.breaks:
			if j.enabled == True:
				sys.stdout.write('*')
			else:
				chars = "x.o"
				sys.stdout.write(chars[j.valid + 1])

		breaks = self.breaks[low:high]
		if len(breaks) == 0:
			return 

		if will_fail or self.fucked_run():
			# things didn't work
			l = len(breaks)# 16
			print "Fucked {0}->{1}".format(low, high) 
			if l == 1:
				breaks[0].valid = -1
				return False

			mid = (high + low)/2 

			# if the left side is ok 
			# then we know the right must be fucked
			if not will_fail:
				self.enable_breakp_range(mid,high,False)

			left_ok = self.smart_search(low, mid)
			self.enable_breakp_range(low,mid,False)

			if left_ok: # left side is ok
				# make half the right side active
				n_mid = (mid+high)/2
				if n_mid == mid:
					n_mid = mid + 1
				self.enable_breakp_range(mid,n_mid,True)
				self.smart_search(mid, high, will_fail=True)
			else:
				# make the whole right side active
				self.enable_breakp_range(mid,high,True)
				self.smart_search(mid, high)

			print "Leaving {0}->{1}".format(low, high) 
			return False
		else:
			for breakp in self.breaks[low:high]:
				breakp.valid = 1
			print "This one is fine {0}->{1}".format(low, high) 
			return True
			
	def fucked_run(self):
		self.fucked = False
		self.gdb_run("run")
		return self.fucked

	def load_from_file(self):
		break_data = []
		with open(self.break_file , "r") as f:
			break_data = json.loads(''.join(f.readlines()))
		return break_data

	def save_breaks(self):
		dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i != y ])
		with open(self.break_file , "w") as f:
			f.write(
				json.dumps( # dump it in nice json
					[ 
						j.dump()
						for j in self.breaks if j.valid == 1
					],
					indent=4 # 4 indent is the best indent
				)
			)
		# may as well save this becasue it's kinda interesting
		with open(self.bad_break_file , "w") as f:
			f.write(
				json.dumps( # dump it in nice json
						[
							j.dump()
							for j in self.breaks if j.valid != 1
						], # only the invalid ones
					indent=4 # 4 indent is the best indent
				)
			)

		for breakp in self.breaks:
			if breakp.valid == 1:
				breakp.enabled = True
			else:
				# does breakp need to be freed?? probs not
				self.breaks.remove(breakp)

	def get_breaks(self):
		# load all the break points
		# on the first few runs work out the bad ones
		# disable those and then keep on for clear fuzzing
		file_exists = os.path.isfile(self.break_file)
		# probs check hash of the binary for total completness
		break_data = self.load_from_file() if file_exists else self.extract_breaks()
		self.breaks = [self.breakClass(bd, self.peda) for bd in break_data]
		self.enable_breakp_range()
		# self.smart_search(0,len(self.breaks))
		if not file_exists:
			self.save_breaks()

	def fuzz(self):
		self.run_count += 1
		return

	def prep(self, _report_file):
		self.report_file = _report_file
		return

	def report(self, line):
		"""
			Add to the report
		"""
		self.report_buffer += line + '\n'
		self.flush_report()
		return

	def flush_report(self):
		with open(self.report_file, 'a') as f:
			f.write(self.report_buffer + '\n')
		self.report_buffer = ""
		return

