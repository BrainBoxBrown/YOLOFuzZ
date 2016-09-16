#!/usr/bin/python

# this does the analysis :)

import json
import networkx as nx
from networkx.readwrite import json_graph
import http_server 
import os
# some code was stolen from 
# https://github.com/networkx/networkx/blob/master/examples/javascript/force

def dump(obj):
  for attr in dir(obj):
	print ("obj.{0} = {1}".format(attr, getattr(obj, attr)))


# create a graph based on the jmps


def load_jmp_trace(file_name):
	"""
		Lets start out simple and just load all the jmps and start 
		mapping them out
	"""
	jmps = []
	# hey maybe add the opcode to the report pls
	with open(file_name) as report:
		for line in report.readlines():
			if 'jmp' in line:
				jmp = {}
				# Hit  jmp:0x10000fd84 mod:False
				jmp["did_hit"] = "Hit" in line
				jmp["address"] = line[line.index(':') + 1:line.index('mod') -1]
				jmp["mod"] = 'True' in line
				jmps.append(jmp)
	return jmps

def visualise(jmps):

	DG=nx.DiGraph()
	# this d3 example uses the name attribute for the mouse-hover value,
	# so add a name to each node
	# for jmp in jmps:
	addrs = [j["address"] for j in jmps]
	DG.add_nodes_from(addrs)
	prev = addrs[0]
	for j in addrs[1:]:
		if prev in DG.predecessors(j):
			DG.edge[prev][j]['weight'] += 1
		else:
			DG.add_edge(prev, j, weight=1)
		prev = j
	for n in DG:
		DG.node[n]['name'] = n
		DG.node[n]['predecessors'] = len(DG.predecessors(n) + DG.successors(n))
	# write json formatted data
	d = json_graph.node_link_data(DG) # node-link format to serialize
	# write json
	json.dump(d, open('force/force.json','w'), indent=4)
	print('Wrote node-link JSON data to force/force.json')
	# open URL in running web bro
	http_server.load_url('force/force.html')
	print('Or copy all files in force/ to webserver and load force/force.html')


jmps = []
dirName = '../reports/qlmanage/'
# jmps = load_jmp_trace(dirName + os.listdir(dirName)[1])
for filename in os.listdir(dirName):
	jmps += load_jmp_trace(dirName + filename)

visualise(jmps)








