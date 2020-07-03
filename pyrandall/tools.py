import itertools

# module for alias methods

def flatten(alist):
    return list(itertools.chain.from_iterable(alist))
