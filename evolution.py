from queue import Queue
from copy import deepcopy
from random import random, randint, uniform, choice
from math import isnan, isinf

from functions import funcs
from datastructures import Tree, Node

def evolve(target, numinputs):
	NUMTREES = 1000000
	NUMTREETRIALS = 20

	cache = {}

	global_min = None

	sampleMin = -10000000#-1e10#30
	sampleMax = 10000000#1e10#30

	inputs = [Node(None, [0,1], i) for i in range(numinputs)]

	def rand():
		# XXX Use hyperopt to perform testing? markov sampling?
		#return (random()-0.5)*2000
		return uniform(sampleMin, sampleMax)
		#return uniform(-2000, 2000)

	q = Queue()

	champions = set()

	bestlist = set()

	trees_generated = 0

	running_average_error = 0

	treeindex = 0

	def print_statistics():
		print("Trees tested:", treeindex,"Generated: ", trees_generated)
		print("Queue length: ", q.qsize(), "Bestlist:", len(bestlist), "Champions:", len(champions))
		print("Global minimum:", global_min, "Running average: ", running_average_error)

	for treeindex in range(NUMTREES):

		if treeindex % 10000 == 0:
			print_statistics()

		if q.empty() or random() < 0.25:
			r = random()
			if r < 0.025 and len(champions) > 0:
				# TODO don't try same datapoints if sampling range is small, test edge cases?
				tree = choice(tuple(champions))
				newtree = deepcopy(tree)
				newtree.mutate()
				q.put(newtree)
			elif r < 0.05 and len(bestlist) > 0:
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
			prevstats = {"terr": 0, "aerr": 0, "fails": 0, "tries": 0, "sfails": 0}

		total_error = 0

		fails = 0
		simul_fails = 0
		for trials in range(NUMTREETRIALS):
			inputvalues = [rand() for i in range(len(inputs))]
			# TODO outputS?

			model_failed = False
			target_failed = False

			try:
				treeoutput = tree.evaluate(inputvalues)
			except (ZeroDivisionError, OverflowError):
				# TODO only fail if target does not raise the same!
				model_failed = True

			try:
				targetoutput = target(*inputvalues)
			except (ZeroDivisionError, OverflowError):
				target_failed = True

			# Assuming same error, doesn't have to be!
			if model_failed and target_failed:
				simul_fails += 1
			elif model_failed or target_failed:
				fails += 1
			else:
				delta = abs(targetoutput-treeoutput)
				#print(delta)
				#print(treeoutput, targetoutput, delta)
				total_error += delta

		#print(simul_fails, fails, total_error)
		#if simul_fails + fails == NUMTREETRIALS:
		#	continue

		average_error = total_error/NUMTREETRIALS

		running_average_steepness = 0.95
		running_average_error = running_average_error * running_average_steepness + average_error * (1 - running_average_steepness)
		if isnan(running_average_error) or isinf(running_average_error):
			running_average_error = 0
		#print(treeindex, average_error)

		combined_fails = fails + prevstats["fails"]
		combined_total_error = total_error + prevstats["terr"]
		combined_tries = NUMTREETRIALS + prevstats["tries"]
		combined_sfails = simul_fails + prevstats["sfails"]

		# TODO measure evaluation/tree complexity

		stats = {"terr": combined_total_error, "aerr": combined_total_error/combined_tries, "fails": combined_fails, "sfails": combined_sfails, "tries": combined_tries}

		if fails + simul_fails < NUMTREETRIALS and (global_min is None or average_error < global_min or average_error == 0):
			global_min = average_error

			print_statistics()

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

			#else:
			# XXX do not mutate champions?
			for c in range(5):
				newtree = deepcopy(tree)
				newtree.mutate()
			q.put(newtree)
		else:
			if average_error < running_average_error:
				for i in range(2):
					if random() > q.qsize()/50:
						newtree = deepcopy(tree)
						newtree.mutate()
						q.put(newtree)
