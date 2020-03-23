from random import randint, choice, random, uniform, shuffle
from copy import deepcopy

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

		self.value = None

		# Subtree mutation
		for child in self.children:
			child.mutate(tree, depth+1)

		if random() < 0.1:
			shuffle(self.children)

		# Node mutation
		if random() < 0.25:
			self.f = tree.getRandomInOutNode(*self.nio).f

		# Node deletion
		if random() < 0.05:
			if len(self.children) > 0:
				subtree = choice(self.children)
				if len(subtree.children) == len(self.children):
					self.children = subtree.children


		# Node insertion
		if depth < 10 and random() < 0.05/(2**depth) and self.nio == [2,1]:
			#print(tree, depth)
			subtree = Node(self.f, deepcopy(self.nio))#deepcopy(self.f)
			self.f = tree.getRandomInOutNode(2,1).f
			self.nio = [2,1]
			subtree.children = self.children#deepcopy(self.children)
			self.children = [subtree, tree.getRandomInOutNode(0,1)]#deepcopy(self)

		# TODO: node switch?


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
				missing = max(0, node.nio[0]-len(node.children))
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
