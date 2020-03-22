from random import random

class Node:
    def __init__(self):
        self.children = []

    def mutate(self):

        if random() < 0.1:
            child = Node()
            child.children = self.children
            self.children = [child, Node()]

        for child in self.children:
            child.mutate()

    def print(self, depth=0):
        prefix = "\t" * depth
        print(prefix + str(self))
        l = []
        l.append(str(self))
        for child in self.children:
            l += child.print(depth + 1)

        return l

root = Node()

for i in range(10):
    root.mutate()

l = root.print()
print(len(l), len(set(l)))
