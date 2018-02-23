import sys
import types

from functools import partial
from ops import ops



class AmbiguousType(object):
  pass


def ambiguous_method(func, *args):
  wrapper = partial(func, *args)

  class AmbiguousMethod(AmbiguousType):
      def __call__(self, *args):
        return wrapper(*args)

  for op in ops:
    def exec_op(op, *args):
      return getattr(wrapper(), op)(*args)

    setattr(AmbiguousMethod, op, partial(exec_op, op))

  return AmbiguousMethod()


# instance method
def ambiguous_instancemethod(func):
  class AmbiguousInstanceMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      if obj:
        return ambiguous_method(func, obj)

      # return unbound method
      return types.MethodType(func, None, objtype)

  return AmbiguousInstanceMethod()


# class method
def ambiguous_classmethod(func):
  class AmbiguousClassMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      return ambiguous_method(func, objtype)

  return AmbiguousClassMethod()


# static method
ambiguous_staticmethod = ambiguous_method


# export ambiguous methods
__all__ = [ x for x in dir() if x.startswith('ambiguous_') ]