# rantree - function reconstruction

Given an (possibly unknown) target function over the reals with n inputs, tries to find an expression tree that best approximates it.

The target function is randomly sampled, the expression trees are evolved (transformed and selected) in a way that prefers lower average error.

Expression tree transformation:

- node insertion
- node mutation
- node shuffling
- node deletion

Expression tree nodes:

- function inputs
- addition, multiplication, exponentiation, division
- constants
