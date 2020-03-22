from random import randint, choice, random, uniform
from math import sin, cos, tan, pi, e
from time import time
from queue import Queue
from copy import deepcopy

def scaledrandom():
	return (random()-0.5)*4

def mul(a,b):
	return a*b

def sum(a,b):
	return a+b

def div(a,b):
	return a/b

def exp(a,b):
	return a**b

def w_const(n):
	def const():
		return n
	return const

class Node:
	def __init__(self, f, nio, input=None):
		self.f = f
		self.nio = nio
		self.children = []
		self.value = None
		self.input = input

	def evaluate(self):
		childvalues = [child.evaluate() for child in self.children]

		if callable(self.f):
			self.value = self.f(*childvalues)
		else:
			return self.f

		return self.value

	def viz(self, depth=0):
		prefix = "\t" * depth
		if callable(self.f):
			print(prefix + str(self.f.__name__))
		else:
			if self.input is not None:
				print(prefix + f"[{self.input}]")
			else:
				print(prefix + f"{self.f}")

		for child in self.children:
			child.viz(depth+1)

	def expr(self):
		if callable(self.f):
			args = ','.join([child.expr() for child in self.children])
			return self.f.__name__ + f"({args})"
		else:
			if self.input is not None:
				return f"[{self.input}]"
			else:
				return f"{self.f}"

	def mutate(self, tree, depth=0):


		for child in self.children:
			child.mutate(tree, depth+1)

		if random() < 0.25:
			#print("mutate")
			self.f = tree.getRandomInOutNode(*self.nio).f


		if random() < 0.05:
			if len(self.children) > 0:
				subtree = choice(self.children)
				if len(subtree.children) == len(self.children):
					self.children = subtree.children
		# node switch?

		#node insertion
		if depth < 2 and random() < 0.1/(10**depth) and self.nio == [2,1]:
			#print(tree, depth)
			subtree = Node(self.f, deepcopy(self.nio))#deepcopy(self.f)
			self.f = tree.getRandomInOutNode(2,1).f
			self.nio = [2,1]
			subtree.children = self.children#deepcopy(self.children)
			self.children = [subtree, tree.getRandomInOutNode(0,1)]#deepcopy(self)

funcs = {
	#inputs, outputs
	#sin: [1,1],
	#cos: [1,1],
	#tan: [1,1],
	#scaledrandom: [0,1],
	#time: [0,1],#should be fixed during evaluation
	mul: [2,1],
	sum: [2,1],
	div: [2,1],
	exp: [2,1],

	Node(-1, [0,1]): [0,1],
	Node(2, [0,1]): [0,1],

	#w_const(pi): [0,1],
	#w_const(e): [0,1],

}


class Tree:
	def __init__(self, funcs, inputs):

		self.funcs = funcs
		self.inputs = inputs

		self.possible_nodes = {**funcs, **{inp:[0,1] for inp in self.inputs}}

		self.root = None
		self.nodes = []


	def getOut(self, n):
		return [item for item in self.possible_nodes.items() if item[1][1]==n]

	def getIn(self, n):
		return [item for item in self.possible_nodes.items() if item[1][0]==n]

	def getInOut(self, a, b):
		return [item for item in self.possible_nodes.items() if item[1][0]==a and item[1][1]==b]

	def getRandomInOutNode(self, a, b):
		f, nio = choice(self.getInOut(a,b))
		if isinstance(f, Node):
			return f
		return Node(f, nio)

	def getRandomInNode(self, n):
		f, nio = choice(self.getIn(n))
		if isinstance(f, Node):
			return f
		return Node(f, nio)

	def getRandomOutNode(self, n):
		f, nio = choice(self.getOut(n))
		if isinstance(f, Node):
			return f
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
			self.inputs[i].f = inputvalue

		return self.root.evaluate()

	def viz(self):
		self.root.viz()

	def expr(self):
		return self.root.expr()

	def mutate(self):
		self.root.mutate(self)

def AtimesBplusC(a,b,c):
	return a*b+c

def AtimesBtimesC(a,b,c):
	return a*b*c

def AsqrtB(a,b,c):
	return b**(1/a)

def arbitrary(a,b,c):
	return (a+b)**2+c#a*(b-c)+b/a

target = arbitrary#AsqrtB#AtimesBtimesC#AtimesBplusC

inputs = [Node(None, [0,1], i) for i in range(3)]

NUMTREES = 1000000
NUMTREETRIALS = 100

cache = {}

global_min = None

sampleMin = -10000000#-1e10#30
sampleMax = 10000000#1e10#30

def rand():
	#return (random()-0.5)*2000
	return uniform(sampleMin, sampleMax)#use hyperopt to perform testing? markov sampling?
	#return uniform(-2000, 2000)

q = Queue()

champions = set()

bestlist = set()

trees_generated = 0

for treeindex in range(NUMTREES):

	if q.empty():
		if random() < 0.001:

			if random() < 0.5 and len(champions) > 0:
				# TODO don't try same datapoints if sampling range is small, test edge cases?
				tree = choice(tuple(champions))
				newtree = deepcopy(tree)
				newtree.mutate()
				q.put(newtree)
			else:
				tree = choice(tuple(bestlist))
				tree = deepcopy(tree)
				tree.mutate()

		else:
			tree = Tree(funcs, inputs)
			tree.construct(randint(3,20))
			trees_generated += 1
	else:
		#print("Queue:", q.qsize())
		tree = q.get()
		#print("GOT", tree)

	exprstring = str(tree.expr())
	if exprstring in cache:
		prevstats = cache[exprstring]
	else:
		prevstats = {"terr": 0, "aerr": 0, "fails": 0, "tries": 0}

	total_error = 0

	fails = 0
	for trials in range(NUMTREETRIALS):
		inputvalues = [rand() for i in range(len(inputs))]
		# TODO outputS?

		try:
			treeoutput = tree.evaluate(inputvalues)
		except (ZeroDivisionError, OverflowError):
			# TODO only fail if target does not raise the same!
			fails += 1
			continue
		try:
			targetoutput = target(*inputvalues)
		except OverflowError:
			fails += 1
			continue

		#print("TREE:", tree.nodes)

		delta = abs(targetoutput-treeoutput)

		#print(treeoutput, targetoutput, delta)

		total_error += delta

	average_error = total_error/NUMTREETRIALS
	#print(treeindex, average_error)

	combined_fails = fails + prevstats["fails"]
	combined_total_error = total_error + prevstats["terr"]
	combined_tries = NUMTREETRIALS + prevstats["tries"]

	stats = {"terr": combined_total_error, "aerr": combined_total_error/combined_tries, "fails": combined_fails, "tries": combined_tries}

	if fails == 0 and (global_min is None or average_error < global_min or average_error == 0):
		global_min = average_error
		print("Trees generated: ", trees_generated)
		print("Queue length: ", q.qsize(), "Bestlist:", len(bestlist), "Champions:", len(champions))
		print("New minimum: ", global_min)

		bestlist.add(tree)
		#tree.viz()
		print(tree.expr())

		cache[str(tree.expr())] = stats
		if global_min == 0:
			#might be just luck, not all datapoints! keep testing

			if tree not in champions:
				print("FOUND!")
				champions.add(tree)

			#q.put(tree)
			print("CACHE:")
			for t,s in cache.items():
				print(t, s)
			# TODO still continue search, minimize nodes
			#break

		else:
			# XXX do not mutate champions?
			for c in range(50):
				newtree = deepcopy(tree)
				newtree.mutate()
				q.put(newtree)
