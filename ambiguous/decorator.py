import types
from functools import partial, wraps

from .inspector import same_method


__all__ = [ 'decorator' ]


"""
Enable a decorator to accept args and kwargs.  Positional args
may not be callable when used via `@decorator`.
"""
def decorator(decorator_fn):
  @wraps(decorator_fn)
  def wrapper(*args, **kwargs):
    assert args or kwargs

    if args:
      if callable(args[0]):
        # apply desired decorator
        return decorator_fn(*args, **kwargs)

      # passed an arg, but not the function to decorate. wrap
      # and wait for more.
      @wraps(decorator_fn)
      def arg_wrapper(*more_args, **more_kwargs):
        if more_args and callable(more_args[0]):
          if len(more_args) > 1:
            # arg order is ambiguous
            raise ValueError(
              'expecting either callable or args, not both: %s' % str(more_args)
            )

          # prepend callable
          new_args = more_args + args
        else:
          # append additional args
          new_args = args + more_args

        # merge in new kwargs
        new_kwargs = dict(kwargs, **more_kwargs)

        return wrapper(*new_args, **new_kwargs)

      return arg_wrapper

    # given kwargs and still need function
    @wraps(decorator_fn)
    def kwarg_wrapper(*args, **more_kwargs):
      return wrapper(*args, **dict(kwargs, **more_kwargs))
    return kwarg_wrapper


  return wrapper


def is_self(wrapper, *args):
  if 0 == len(args):
    return False

  if type(wrapper) == types.MethodType:
    # convert unbound into function
    # eg. <unbound method Foo.bar> => <function bar>
    wrapper = wrapper.im_func

  self = args[0]

  if type(self) != types.InstanceType:
    return False

  if type(self.__class__) != types.ClassType:
    return False

  # does bound instance method exist
  if not hasattr(self, wrapper.__name__):
    return False

  # compare wrapper with unbound class method
  return same_method(
    wrapper,
    getattr(self, wrapper.__name__).im_func
  )

  member_fn = dict(inspect.getmembers(self))[fn.__name__]
