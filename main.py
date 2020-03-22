from evolution import evolve

def AtimesBplusC(a,b,c):
	return a*b+c

def AtimesBtimesC(a,b,c):
	return a*b*c

def AsqrtB(a,b,c):
	return b**(1/a)

def arbitrary(a,b,c):
	return (a+b)**2+c#a*(b-c)+b/a

evolve(arbitrary, 3)
