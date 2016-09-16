import os
import re
import gdb
import sys
import json
import random

from BinMod import BinMod, FuzzBreakpoint
from objdump_wrapper import *
opcodes = {  
	"jo":{  
		"meaning":"if overflow",
		"flags":"OF = 1",
		"short":[0x70],
		"near":[  
			0x0F,
			0x80
		],
		"opposite":"jno"
	},
	"jno":{  
		"meaning":"if not overflow",
		"flags":"OF = 0",
		"short":[0x71],
		"near":[  
			0x0F,
			0x81
		],
		"opposite":"jo"
	},
	"js":{  
		"meaning":"if sign",
		"flags":"SF = 1",
		"short":[0x78],
		"near":[  
			0x0F,
			0x88
		],
		"opposite":"jns"
	},
	"jns":{  
		"meaning":"if not sign",
		"flags":"SF = 0",
		"short":[0x79],
		"near":[  
			0x0F,
			0x89
		],
		"opposite":"js"
	},
	"je":{  
		"meaning":"if equal",
		"flags":"ZF = 1",
		"short":[0x74],
		"near":[  
			0x0F,
			0x84
		],
		"opposite":"jne"
	},
	"jz":{  
		"meaning":"if zero",
		"flags":"ZF = 1",
		"short":[0x74],
		"near":[  
			0x0F,
			0x84
		],
		"opposite":"jnz"
	},
	"jne":{  
		"meaning":"if not equal",
		"flags":"ZF = 0",
		"short":[0x75],
		"near":[  
			0x0F,
			0x85
		],
		"opposite":"je"
	},
	"jnz":{  
		"meaning":"if not zero",
		"flags":"ZF = 0",
		"short":[0x75],
		"near":[  
			0x0F,
			0x85
		],
		"opposite":"jz"
	},
	"jbe":{  
		"meaning":"if below or equal ",
		"signedness":"unsigned",
		"flags":"CF = 1 or ZF = 1",
		"short":[0x76],
		"near":[  
			0x0F,
			0x86
		],
		"opposite":"jnbe"
	},
	"jna":{  
		"meaning":"if not above",
		"signedness":"unsigned",
		"flags":"CF = 1 or ZF = 1",
		"short":[0x76],
		"near":[  
			0x0F,
			0x86
		],
		"opposite":"ja"
	},
	"ja":{  
		"meaning":"if above ",
		"signedness":"unsigned",
		"flags":"CF = 0 and ZF = 0",
		"short":[0x77],
		"near":[  
			0x0F,
			0x87
		],
		"opposite":"jna"
	},
	"jnbe":{  
		"meaning":"if not below or equal",
		"signedness":"unsigned",
		"flags":"CF = 0 and ZF = 0",
		"short":[0x77],
		"near":[  
			0x0F,
			0x87
		],
		"opposite":"jbe"
	},
	"jl":{  
		"meaning":"if less ",
		"signedness":"signed",
		"flags":"SF <> OF",
		"short":[0x7C],
		"near":[  
			0x0F,
			0x8C
		],
		"opposite":"jnl"
	},
	"jnge":{  
		"meaning":"if not greater or equal	",
		"signedness":"signed",
		"flags":"SF <> OF",
		"short":[0x7C],
		"near":[  
			0x0F,
			0x8C
		],
		"opposite":"jge"
	},
	"jge":{  
		"meaning":"if greater or equal  ",
		"signedness":"signed",
		"flags":"SF = OF",
		"short":[0x7D],
		"near":[  
			0x0F,
			0x8D
		],
		"opposite":"jnge"
	},
	"jnl":{  
		"meaning":"if not less	",
		"signedness":"signed",
		"flags":"SF = OF",
		"short":[0x7D],
		"near":[  
			0x0F,
			0x8D
		],
		"opposite":"jl"
	},
	"jle":{  
		"meaning":"if less or equal  ",
		"signedness":"signed",
		"flags":"ZF = 1 or SF <> OF",
		"short":[0x7E],
		"near":[  
			0x0F,
			0x8E
		],
		"opposite":"jnle"
	},
	"jng":{  
		"meaning":"if not greater	",
		"signedness":"signed",
		"flags":"ZF = 1 or SF <> OF",
		"short":[0x7E],
		"near":[  
			0x0F,
			0x8E
		],
		"opposite":"jg"
	},
	"jg":{  
		"meaning":"if greater ",
		"signedness":"signed",
		"flags":"ZF = 0 and SF = OF",
		"short":[0x7F],
		"near":[  
			0x0F,
			0x8F
		],
		"opposite":"jng"
	},
	"jnle":{  
		"meaning":"if not less or equal",
		"signedness":"signed",
		"flags":"ZF = 0 and SF = OF",
		"short":[0x7F],
		"near":[  
			0x0F,
			0x8F
		],
		"opposite":"jle"
	},
	"jp":{  
		"meaning":"if parity",
		"flags":"PF = 1",
		"short":[0x7A],
		"near":[  
			0x0F,
			0x8A
		],
		"opposite":"jnp"
	},
	"jpe":{  
		"meaning":"if parity even",
		"flags":"PF = 1",
		"short":[0x7A],
		"near":[  
			0x0F,
			0x8A
		],
		"opposite":"jpo"
	},
	"jnp":{  
		"meaning":"if not parity",
		"flags":"PF = 0",
		"short":[0x7B],
		"near":[  
			0x0F,
			0x8B
		],
		"opposite":"jp"
	},
	"jpo":{  
		"meaning":"if parity odd",
		"flags":"PF = 0",
		"short":[0x7B],
		"near":[  
			0x0F,
			0x8B
		],
		"opposite":"jpe"
	},
	"jb":{  
		"meaning":"if below",
		"signedness":"unsigned",
		"flags":"CF = 1",
		"short":[0x72],
		"near":[  
			0x0F,
			0x82
		],
		"opposite":"jnb"
	},
	"jnae":{  
		"meaning":"if not above or equal",
		"signedness":"unsigned",
		"flags":"CF = 1",
		"short":[0x72],
		"near":[  
			0x0F,
			0x82
		],
		"opposite":"jae"
	},
	"jc":{  
		"meaning":"if carry",
		"signedness":"unsigned",
		"flags":"CF = 1",
		"short":[0x72],
		"near":[  
			0x0F,
			0x82
		],
		"opposite":"jnc"
	},
	"jnb":{  
		"meaning":"if not below",
		"signedness":"unsigned",
		"flags":"CF = 0",
		"short":[0x73],
		"near":[  
			0x0F,
			0x83
		],
		"opposite":"jb"
	},
	"jae":{  
		"meaning":"if above or equal",
		"signedness":"unsigned",
		"flags":"CF = 0",
		"short":[0x73],
		"near":[  
			0x0F,
			0x83
		],
		"opposite":"jnae"
	},
	"jnc":{  
		"meaning":"if not carry",
		"signedness":"unsigned",
		"flags":"CF = 0",
		"short":[0x73],
		"near":[  
			0x0F,
			0x83
		],
		"opposite":"jc"
	}
}


# j + "->" + jmps[jmps[j]["opposite"]]["opposite"]
# I have checked every one is it's inverse


# ignore these because they don't have an inverse
# JCXZ if %CX register is 0 
# JECXZ if %ECX register is 0
# E3


class JmpBreakpoint (FuzzBreakpoint):
	"""
		flip jmps

		if you want to load a modded jmp
		you'll need to add a flip to the init 
		function and invert mod back
		k :)
	"""
	def flip(self):
		loaded_jmp = opcodes[self.opcode]
		opposite_op = loaded_jmp["opposite"]
		opposite_code = ""	
		op_bytes = []
		if self.bytes[0] == loaded_jmp["short"][0]:
			op_bytes = opcodes[opposite_op]["short"]
			opposite_code = hex(op_bytes[0])
		elif self.bytes[1] == loaded_jmp["near"][1]:
			op_bytes = opcodes[opposite_op]["near"]
			# have to reverse order for little endian apparently
			opposite_code = "0x" + ''.join([chr(x).encode('hex') for x in op_bytes[::-1]])
		else:
			print self.bytes
			print loaded_jmp
			raise "failed to match bytes!!"
			return
		cmd = "patch {0} {1}".format(str(self.address), str(opposite_code))		
		self.report(cmd) # add the cmds to the report			
		self.gdb_run(cmd)
		self.mod = not self.mod
		self.opcode = opposite_op
		self.bytes = op_bytes


	def stop (self):
		next_addr = self.peda.testjump()
		msg = "Hit  " if next_addr else "Miss "
		msg += "jmp:{loc} mod:{mod}".format(loc=self.address,mod=self.mod)
		self.report(msg)
		return False




class JmpFlip( BinMod ):

	def __init__(self, _peda, report_folder):
		self.breakClass = JmpBreakpoint
		self.break_file = report_folder + "/jmps.json"
		self.bad_break_file = report_folder + "/bad_jmps.json"
		super(JmpFlip, self).__init__(_peda, report_folder)

	def extract_breaks(self):
		"""
			Extract all the friendly looking jmps
		"""
		breaks = super(JmpFlip, self).extract_breaks()
		# move this to a config file
		bad_jmps = [
			"tm_clones",
			"libc",
			"frame_dummy",
			"init",
			"dtors"
		]
		# dump all the instructions
		dump = objdump_extract(self.my_config["prog"])
		# get all the conditional jumps
		con_jmps = [
			op for pos, op in enumerate(dump)
				if re.match(r'j[^m]',op["opcode"]) and (
					"cmp" in [o["opcode"] for o in dump[pos-4:pos]] or 
					"test" in [o["opcode"] for o in dump[pos-4:pos]] )]
		# filter out the irrelevant ones
		#      all jmps in con_jmps if not any(word in j["args"][0] is a word in bad_jmps)]
		jmps = [j for j in con_jmps if not any(word in j["args"][0] for word in bad_jmps)]
		return breaks + [j for j in jmps if j["opcode"] in opcodes] # only get ones we can flip

	def prep(self, _report_file):
		super(JmpFlip, self).prep(_report_file)
		[jmp.report_to_file(_report_file) for jmp in self.breaks]

	def fuzz(self):
		"""
			This runs just after we start
			flip some jumps
		"""
		super(JmpFlip, self).fuzz()

		# for all the jumps set the report file todo
		for jmp in self.breaks:
			if random.randint(0,100) != 0:
				continue	
			jmp.flip()	

	def flip_range(self,low=0,high=-1,active=True):

		if high == -1:
			high = len(self.breaks)
		for breakp in self.breaks[low:high]:
			breakp.flip()

	# def fuck_shit_up(self):
	# 	gdb.events.exited.connect(self.exit_handler)
	# 	gdb.events.stop.connect(self.stop_handler)
	# 	for b in self.breaks:
	# 		b.jLevel = 0
	# 	self.gdb_run("start")
	# 	self.flip_range()# flips everything
	# 	self.smart_fuck(0, len(self.breaks))
	# 	gdb.events.exited.disconnect(self.exit_handler)
	# 	gdb.events.stop.disconnect(self.stop_handler)

	
	# def smart_fuck(self, low, high):
	# 	"""
	# 	ffffuuuuuuuuuuuuuuuuuuuckkkkkkkkk 
	# 	"""

	# 	for j in self.breaks:
	# 		if j.mod == True:
	# 			sys.stdout.write('*')
	# 		else:
	# 			chars = "x.o"
	# 			sys.stdout.write(chars[j.jLevel + 1])

	# 	breaks = self.breaks[low:high]
	# 	if len(breaks) == 0:
	# 		return 

	# 	if not self.fucked_run():
	# 		self.gdb_run("start")
	# 		# things didn't work
	# 		l = len(breaks)# 16
	# 		print "Fucked {0}->{1}".format(low, high) 
	# 		if l == 1:
	# 			breaks[0].jLevel = -1
	# 			return False

	# 		mid = (high + low)/2 

	# 		# if the left side is ok 
	# 		# then we know the right must be fucked

	# 		self.flip_range(mid,high,False)

	# 		left_ok = self.smart_search(low, mid)
	# 		self.flip_range(low,mid,False)

	# 			# make the whole right side active
	# 		self.flip_range(mid,high,True)
	# 		self.smart_search(mid, high)

	# 		print "Leaving {0}->{1}".format(low, high) 
	# 		return False
	# 	else:
	# 		for breakp in self.breaks[low:high]:
	# 			breakp.jLevel = 1
	# 		print "This one is fine {0}->{1}".format(low, high) 
	# 		return True


	def finish(self):
		super(JmpFlip, self).finish()



