def fresh_var(name):
    counter = getattr(fresh_var, "_counter", 0) + 1
    setattr(fresh_var, "_counter", counter)
    return name + "_" + str(counter)
