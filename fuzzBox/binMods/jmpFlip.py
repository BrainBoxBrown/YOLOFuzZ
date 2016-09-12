import re
import gdb
from BinMod import BinMod
from objdump_wrapper import *
import random
opcodes = {  
    "jo":{  
        "meaning":"if overflow",
        "flags":"OF = 1",
        "short":0x70,
        "near":[  
            0x0F,
            0x80
        ],
        "opposite":"jno"
    },
    "jno":{  
        "meaning":"if not overflow",
        "flags":"OF = 0",
        "short":0x71,
        "near":[  
            0x0F,
            0x81
        ],
        "opposite":"jo"
    },
    "js":{  
        "meaning":"if sign",
        "flags":"SF = 1",
        "short":0x78,
        "near":[  
            0x0F,
            0x88
        ],
        "opposite":"jns"
    },
    "jns":{  
        "meaning":"if not sign",
        "flags":"SF = 0",
        "short":0x79,
        "near":[  
            0x0F,
            0x89
        ],
        "opposite":"js"
    },
    "je":{  
        "meaning":"if equal",
        "flags":"ZF = 1",
        "short":0x74,
        "near":[  
            0x0F,
            0x84
        ],
        "opposite":"jne"
    },
    "jz":{  
        "meaning":"if zero",
        "flags":"ZF = 1",
        "short":0x74,
        "near":[  
            0x0F,
            0x84
        ],
        "opposite":"jnz"
    },
    "jne":{  
        "meaning":"if not equal",
        "flags":"ZF = 0",
        "short":0x75,
        "near":[  
            0x0F,
            0x85
        ],
        "opposite":"je"
    },
    "jnz":{  
        "meaning":"if not zero",
        "flags":"ZF = 0",
        "short":0x75,
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
        "short":0x76,
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
        "short":0x76,
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
        "short":0x77,
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
        "short":0x77,
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
        "short":0x7C,
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
        "short":0x7C,
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
        "short":0x7D,
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
        "short":0x7D,
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
        "short":0x7E,
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
        "short":0x7E,
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
        "short":0x7F,
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
        "short":0x7F,
        "near":[  
            0x0F,
            0x8F
        ],
        "opposite":"jle"
    },
    "jp":{  
        "meaning":"if parity",
        "flags":"PF = 1",
        "short":0x7A,
        "near":[  
            0x0F,
            0x8A
        ],
        "opposite":"jnp"
    },
    "jpe":{  
        "meaning":"if parity even",
        "flags":"PF = 1",
        "short":0x7A,
        "near":[  
            0x0F,
            0x8A
        ],
        "opposite":"jpo"
    },
    "jnp":{  
        "meaning":"if not parity",
        "flags":"PF = 0",
        "short":0x7B,
        "near":[  
            0x0F,
            0x8B
        ],
        "opposite":"jp"
    },
    "jpo":{  
        "meaning":"if parity odd",
        "flags":"PF = 0",
        "short":0x7B,
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
        "short":0x72,
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
        "short":0x72,
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
        "short":0x72,
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
        "short":0x73,
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
        "short":0x73,
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
        "short":0x73,
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


class JmpFlip( BinMod ):

	def get_jmps(self):
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
		con_jmps = [op for op in dump if re.match(r'j[^m]',op["opcode"])]
		# filter out the irrelevant ones
		#      all jmps in con_jmps if not any(word in j["args"][0] is a word in bad_jmps)]
		jmps = [j for j in con_jmps if not any(word in j["args"][0] for word in bad_jmps)]
		return jmps
	
	def __init__(self, _peda):
		super(JmpFlip, self).__init__(_peda)
		self.jmps = self.get_jmps()
		# fuck all the jmps
		# self.gdb_run()
	def prep(self):
		"""
			This runs just after we start
			flip some jumps
		"""
		cmds = ""
		for jmp in self.jmps:
			if random.randint(0,3) != 0:
				continue

			loaded_jmp = opcodes[jmp["opcode"]]
			opposite_op = loaded_jmp["opposite"]
			address = jmp["address"]
			opposite_code = ""
			if jmp["bytes"][0] == loaded_jmp["short"]:
				opposite_code = hex(opcodes[opposite_op]["short"])
			elif jmp["bytes"][1] == loaded_jmp["near"][1]:
				op_bytes = opcodes[opposite_op]["near"]
				opposite_code = "0x" + ''.join([chr(x).encode('hex') for x in op_bytes])

			print address
			print opposite_code
			print "0x" + ''.join([chr(x).encode('hex') for x in jmp["bytes"]])
			cmd = "patch {0} {1}".format(str(address), str(opposite_code))
			print cmd 
			print self.gdb_run(cmd)
			cmds += cmd + '\n'
		return cmds





	def update(self):
		return super(JmpFlip, self).update()



