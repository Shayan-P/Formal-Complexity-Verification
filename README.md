# Formal-Complexity-Verification

This is a tool to automatically analyze the time complexity of recursive functions based on their inputs.

Here we define "time" as the number of function calls that happen.

## Language

This language supports:
- Function definition (similar to python)
- if else statements
- arithmatic operations +, -, *, %
- assert

Each program in this language consists of a list of functions

Each function consist of a list of function calls

Defined Functions are all void

Variables are immutable and can only be integers

### Example

```
def f(n):
	if n <= 0:
	    pass
	else:
        f(n-1)


def g(n, m):
	if n <= 0:
	    pass
	else:
        g(n-1, m)
        f(m)
```

```
def gcd(a, b):
    assert(a >= 0)
    assert(b >= 0)
    if b >= 0:
        pass
    else:
        gcd(b, a%b)
```
