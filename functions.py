from math import sin, cos, tan, pi, e
from datastructures import Node

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
