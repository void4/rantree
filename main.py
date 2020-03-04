from random import randint, choice, random
from math import sin, cos, tan
from time import time

def scaledrandom():
	return (random()-0.5)*4

def mul(a,b):
	return a*b

def sum(a,b):
	return a+b

funcs = {
	#inputs, outputs
	sin: [1,1],
	cos: [1,1],
	#tan: [1,1],
	#scaledrandom: [0,1],
	#time: [0,1],#should be fixed during evaluation
	mul: [2,1],
	sum: [2,1],
}


class Node:
	def __init__(self, f, nio):
		self.f = f
		self.nio = nio
		self.children = []
		self.value = None

	def evaluate(self):
		childvalues = [child.evaluate() for child in self.children]
		self.value = self.f(*childvalues)
		return self.value

	def viz(self, depth=0):
		prefix = "\t" * depth
		if hasattr(self, "f"):
			print(prefix + str(self.f.__name__))
		else:
			print(prefix + f"[{self.index}]")
		for child in self.children:
			child.viz(depth+1)


class FloatInput(Node):
	def __init__(self, index, nio):
		self.index = index
		self.nio = nio
		self.children = []
		self.value = None

	def evaluate(self):
		return self.value

class Tree:
	def __init__(self, funcs, inputs):

		self.funcs = funcs
		self.inputs = [Inp(i, [0,1]) for i, Inp in enumerate(inputs)]

		self.possible_nodes = {**funcs, **{inp:[0,1] for inp in self.inputs}}

		self.root = None
		self.nodes = []


	def getOut(self, n):
		return [item for item in self.possible_nodes.items() if item[1][1]==n]

	def getIn(self, n):
		return [item for item in self.possible_nodes.items() if item[1][0]==n]

	def getRandomInNode(self, n):
		f, nio = choice(self.getIn(n))
		if isinstance(f, FloatInput):#n can be zero
			return f
		else:
			return Node(f, nio)

	def getRandomOutNode(self, n):
		f, nio = choice(self.getOut(n))
		if isinstance(f, FloatInput):
			return f
		else:
			return Node(f, nio)

	def construct(self, maxnodes=10, outputs=1):

		self.root = self.getRandomOutNode(outputs)
		self.nodes.append(self.root)

		while True:
			populated = True
			for node in self.nodes:
				#print(len(self.nodes))
				missing = max(0, node.nio[0]-len(node.children))
				#print(missing)
				for i in range(missing):
					if len(self.nodes) >= maxnodes:
						child = self.getRandomInNode(0)
					else:
						child = self.getRandomOutNode(1)
					node.children.append(child)
					self.nodes.append(child)
					populated = False

			if populated:
				break

	def evaluate(self, inputvalues):

		if len(inputvalues) != len(self.inputs):
			raise ValueError("Input value len doesn't match # of inputs")

		for i, inputvalue in enumerate(inputvalues):
			self.inputs[i].value = inputvalue

		return self.root.evaluate()

	def viz(self):
		self.root.viz()

def target(a,b,c):
	return a*b+c

inputs = [FloatInput, FloatInput, FloatInput]

NUMTREES = 1000
NUMTREETRIALS = 1000

cache = {}

global_min = None

def rand():
	return (random()-0.5)*2000

for treeindex in range(NUMTREES):
	tree = Tree(funcs, inputs)
	tree.construct(randint(3,10))

	total_error = 0

	for trials in range(NUMTREETRIALS):
		inputvalues = [rand() for i in range(len(inputs))]
		# TODO outputS?
		treeoutput = tree.evaluate(inputvalues)
		targetoutput = target(*inputvalues)

		#print("TREE:", tree.nodes)

		delta = abs(targetoutput-treeoutput)

		#print(treeoutput, targetoutput, delta)

		total_error += delta

	average_error = total_error/NUMTREETRIALS
	#print(treeindex, average_error)

	if global_min is None or average_error < global_min:
		global_min = average_error
		print("New minimum: ", global_min)
		tree.viz()
		cache[tree] = average_error
