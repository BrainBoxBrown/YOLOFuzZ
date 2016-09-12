import re
import gdb
from BinMod import BinMod
from objdump_wrapper import *
opcodes = {  
    "JO":{  
        "meaning":"if overflow",
        "flags":"OF = 1",
        "short":0x70,
        "near":[  
            0x0F,
            0x80
        ],
        "opposite":"JNO"
    },
    "JNO":{  
        "meaning":"if not overflow",
        "flags":"OF = 0",
        "short":0x71,
        "near":[  
            0x0F,
            0x81
        ],
        "opposite":"JO"
    },
    "JS":{  
        "meaning":"if sign",
        "flags":"SF = 1",
        "short":0x78,
        "near":[  
            0x0F,
            0x88
        ],
        "opposite":"JNS"
    },
    "JNS":{  
        "meaning":"if not sign",
        "flags":"SF = 0",
        "short":0x79,
        "near":[  
            0x0F,
            0x89
        ],
        "opposite":"JS"
    },
    "JE":{  
        "meaning":"if equal",
        "flags":"ZF = 1",
        "short":0x74,
        "near":[  
            0x0F,
            0x84
        ],
        "opposite":"JNE"
    },
    "JZ":{  
        "meaning":"if zero",
        "flags":"ZF = 1",
        "short":0x74,
        "near":[  
            0x0F,
            0x84
        ],
        "opposite":"JNZ"
    },
    "JNE":{  
        "meaning":"if not equal",
        "flags":"ZF = 0",
        "short":0x75,
        "near":[  
            0x0F,
            0x85
        ],
        "opposite":"JE"
    },
    "JNZ":{  
        "meaning":"if not zero",
        "flags":"ZF = 0",
        "short":0x75,
        "near":[  
            0x0F,
            0x85
        ],
        "opposite":"JZ"
    },
    "JBE":{  
        "meaning":"if below or equal ",
        "signedness":"unsigned",
        "flags":"CF = 1 or ZF = 1",
        "short":0x76,
        "near":[  
            0x0F,
            0x86
        ],
        "opposite":"JNBE"
    },
    "JNA":{  
        "meaning":"if not above",
        "signedness":"unsigned",
        "flags":"CF = 1 or ZF = 1",
        "short":0x76,
        "near":[  
            0x0F,
            0x86
        ],
        "opposite":"JA"
    },
    "JA":{  
        "meaning":"if above ",
        "signedness":"unsigned",
        "flags":"CF = 0 and ZF = 0",
        "short":0x77,
        "near":[  
            0x0F,
            0x87
        ],
        "opposite":"JNA"
    },
    "JNBE":{  
        "meaning":"if not below or equal",
        "signedness":"unsigned",
        "flags":"CF = 0 and ZF = 0",
        "short":0x77,
        "near":[  
            0x0F,
            0x87
        ],
        "opposite":"JBE"
    },
    "JL":{  
        "meaning":"if less ",
        "signedness":"signed",
        "flags":"SF <> OF",
        "short":0x7C,
        "near":[  
            0x0F,
            0x8C
        ],
        "opposite":"JNL"
    },
    "JNGE":{  
        "meaning":"if not greater or equal	",
        "signedness":"signed",
        "flags":"SF <> OF",
        "short":0x7C,
        "near":[  
            0x0F,
            0x8C
        ],
        "opposite":"JGE"
    },
    "JGE":{  
        "meaning":"if greater or equal  ",
        "signedness":"signed",
        "flags":"SF = OF",
        "short":0x7D,
        "near":[  
            0x0F,
            0x8D
        ],
        "opposite":"JNGE"
    },
    "JNL":{  
        "meaning":"if not less	",
        "signedness":"signed",
        "flags":"SF = OF",
        "short":0x7D,
        "near":[  
            0x0F,
            0x8D
        ],
        "opposite":"JL"
    },
    "JLE":{  
        "meaning":"if less or equal  ",
        "signedness":"signed",
        "flags":"ZF = 1 or SF <> OF",
        "short":0x7E,
        "near":[  
            0x0F,
            0x8E
        ],
        "opposite":"JNLE"
    },
    "JNG":{  
        "meaning":"if not greater	",
        "signedness":"signed",
        "flags":"ZF = 1 or SF <> OF",
        "short":0x7E,
        "near":[  
            0x0F,
            0x8E
        ],
        "opposite":"JG"
    },
    "JG":{  
        "meaning":"if greater ",
        "signedness":"signed",
        "flags":"ZF = 0 and SF = OF",
        "short":0x7F,
        "near":[  
            0x0F,
            0x8F
        ],
        "opposite":"JNG"
    },
    "JNLE":{  
        "meaning":"if not less or equal",
        "signedness":"signed",
        "flags":"ZF = 0 and SF = OF",
        "short":0x7F,
        "near":[  
            0x0F,
            0x8F
        ],
        "opposite":"JLE"
    },
    "JP":{  
        "meaning":"if parity",
        "flags":"PF = 1",
        "short":0x7A,
        "near":[  
            0x0F,
            0x8A
        ],
        "opposite":"JNP"
    },
    "JPE":{  
        "meaning":"if parity even",
        "flags":"PF = 1",
        "short":0x7A,
        "near":[  
            0x0F,
            0x8A
        ],
        "opposite":"JPO"
    },
    "JNP":{  
        "meaning":"if not parity",
        "flags":"PF = 0",
        "short":0x7B,
        "near":[  
            0x0F,
            0x8B
        ],
        "opposite":"JP"
    },
    "JPO":{  
        "meaning":"if parity odd",
        "flags":"PF = 0",
        "short":0x7B,
        "near":[  
            0x0F,
            0x8B
        ],
        "opposite":"JPE"
    },
    "JB":{  
        "meaning":"if below",
        "signedness":"unsigned",
        "flags":"CF = 1",
        "short":0x72,
        "near":[  
            0x0F,
            0x82
        ],
        "opposite":"JNB"
    },
    "JNAE":{  
        "meaning":"if not above or equal",
        "signedness":"unsigned",
        "flags":"CF = 1",
        "short":0x72,
        "near":[  
            0x0F,
            0x82
        ],
        "opposite":"JAE"
    },
    "JC":{  
        "meaning":"if carry",
        "signedness":"unsigned",
        "flags":"CF = 1",
        "short":0x72,
        "near":[  
            0x0F,
            0x82
        ],
        "opposite":"JNC"
    },
    "JNB":{  
        "meaning":"if not below",
        "signedness":"unsigned",
        "flags":"CF = 0",
        "short":0x73,
        "near":[  
            0x0F,
            0x83
        ],
        "opposite":"JB"
    },
    "JAE":{  
        "meaning":"if above or equal",
        "signedness":"unsigned",
        "flags":"CF = 0",
        "short":0x73,
        "near":[  
            0x0F,
            0x83
        ],
        "opposite":"JNAE"
    },
    "JNC":{  
        "meaning":"if not carry",
        "signedness":"unsigned",
        "flags":"CF = 0",
        "short":0x73,
        "near":[  
            0x0F,
            0x83
        ],
        "opposite":"JC"
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
		dump = objdump_extract(self.config["prog"])
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
		


	def update(self):
		return super(JmpFlip, self).update()
