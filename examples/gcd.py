def gcd(a, b):
    # assert(a >= 0)
    # assert(b >= 0)
    if b >= 0:
        pass
    else:
        gcd(b, a % b)
