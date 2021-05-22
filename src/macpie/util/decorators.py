from collections import OrderedDict
from functools import partial, update_wrapper
import time


class TrackHistory:
    """Decorator for class methods for tracking history of
    class instance modifications.

    When a class method is decorated with ``@TrackHistory``, each time that
    method is invoked, a record will be added to the class instance's ``_history``
    attribute. The record will include before and after information using
    the instance's ``to_dict()`` method, as well as useful information like
    the method signature used in the invocation and duration of the method call.
    """

    def __init__(self, func):
        # wrap the method
        update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        # method to call
        instance = args[0]  # thanks to __get__ below

        func_name = self.func.__name__
        func_sig = OrderedDict()
        for i, arg in enumerate(args):
            func_sig['arg' + str(i + 1)] = repr(arg)

        for k, v, in kwargs.items():
            func_sig[k] = repr(v)

        if '_history' not in instance.__dict__:
            instance.__dict__['_history'] = []

        history = instance.__dict__['_history']

        record = {
            'func_name': func_name,
            'func_sig': dict(func_sig),
            'before': instance.to_dict(),
            'after' : None,
            'run_time' : None
        }

        history.append(record)

        start_time = time.perf_counter()
        value = self.func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time

        history[-1]['after'] = instance.to_dict()
        history[-1]['run_time'] = f"{run_time:.3f} secs"

        return value

    def __get__(self, instance, owner):
        # By implementing this descriptor method, when __call__ is invoked,
        # this method will be invoked.
        # Wrappers/decorators typically wrap unbound functions, but since
        # this decorator is supposed to decorate ***instance*** methods,
        # we need to pass the bound object as the first argument
        # before __call__ happens.
        return partial(self.__call__, instance)
