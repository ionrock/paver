"""Tasks to help reproduce tasks in Make.

Make is built around the concept of targets that dictate the result of
a task. When you compile some .c file you should get a .o as the
output. Make also describes creating empty targets that can help keep
state and avoid recompilation or doing tasks that take a long time.

In the Python world, we don't have to compile things, but we often do
tasks that could be mitigated if we had some state we could depend
on. For example, creating and bootstrapping a virtualenv for tests is
a good example where the `test` task `needs` the `virtualenv`, but
always running the task is slow in a TDD environment.

For this reason, we have the `make` tasks.
"""
from glob import glob


class PreReq(object):

    def __init__(self, globs):
        self.globs = globs

    def exists(self):
        for pattern in self.globs.split():
            if not glob(pattern):
                return False
        return True

    def out_of_date(self):
        # Until we create a way for tasks to return a target result,
        # we always return True. The prereq is out of date.
        return True

    def met(self):
        return self.exists() and not self.out_of_date()


def prereq(glob):
    reqs = PreReq(glob)

    def inner(func):
        func = func

        def wrapper(*args, **kw):
            if not reqs.met():
                return func(*args, **kw)
            return False
        return wrapper
    return inner
