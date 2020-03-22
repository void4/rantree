

from queue import Queue

from functions import funcs
from random import random, randint, uniform, choice
from copy import deepcopy
from datastructures import Tree, Node


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
	# XXX Use hyperopt to perform testing? markov sampling?
	#return (random()-0.5)*2000
	return uniform(sampleMin, sampleMax)
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
		tree = q.get()

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

	# TODO measure evaluation/tree complexity

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
			# Might be just luck, not all datapoints! Keep testing

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
