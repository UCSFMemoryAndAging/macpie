import collections
import functools
import time


class MethodHistory:
    """Decorator for class methods for tracking history of
    class instance modifications.

    When a class method is decorated with ``@MethodHistory``, each time that
    method is invoked, a record will be added to the class instance's ``_method_history``
    attribute. The record will include before and after information using
    the instance's ``to_dict()`` method, as well as useful information like
    the method signature used in the invocation and duration of the method call.
    """

    def __init__(self, method):
        # wrap the method
        functools.update_wrapper(self, method)
        self.method = method

    def __call__(self, *args, **kwargs):
        # method to call
        instance = args[0]  # thanks to __get__ below

        method_name = self.method.__name__
        method_sig = collections.OrderedDict()
        for i, arg in enumerate(args):
            method_sig["arg" + str(i + 1)] = repr(arg)

        for k, v in kwargs.items():
            method_sig[k] = repr(v)

        if "_method_history" not in instance.__dict__:
            instance._method_history = []

        record = {
            "method_name": method_name,
            "method_sig": dict(method_sig),
            "before": instance.to_dict(),
            "after": None,
            "run_time": None,
        }

        instance._method_history.append(record)

        start_time = time.perf_counter()
        value = self.method(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time

        instance._method_history[-1]["after"] = instance.to_dict()
        instance._method_history[-1]["run_time"] = f"{run_time:.3f} secs"

        return value

    def __get__(self, instance, owner):
        # By implementing this descriptor method, when __call__ is invoked,
        # this method will be invoked.
        # Wrappers/decorators typically wrap unbound functions, but since
        # this decorator is supposed to decorate ***instance*** methods
        # (i.e. bound methods), we need to pass the instance
        # (i.e. bound object) as the first argument before __call__ happens.
        return functools.partial(self.__call__, instance)


class MethodTimer:
    def __init__(self, method):
        functools.update_wrapper(self, method)
        self.method = method

    def __call__(self, *args, **kwargs):
        method_name = self.method.__name__
        method_sig = collections.OrderedDict()
        for i, arg in enumerate(args):
            method_sig["arg" + str(i + 1)] = repr(arg)
        for k, v in kwargs.items():
            method_sig[k] = repr(v)

        instance = args[0]
        if "_method_timer" not in instance.__dict__:
            instance._method_timer = collections.defaultdict(list)

        start_time = time.perf_counter()
        value = self.method(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time

        record = {
            "method_sig": dict(method_sig),
            "run_time_sec": run_time,
            "run_time_sec_str": f"{run_time:.3f} secs",
        }

        instance._method_timer[method_name].append(record)

        return value

    def __get__(self, instance, owner):
        return functools.partial(self.__call__, instance)
