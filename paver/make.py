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

Here is an example that checks if our library is up to date based on
the egg link in the virtualenv.

  from paver.easy import task, options, path
  from paver.make import prereq


  options(venv=path('venv'))


  @task
  @prereq(
      options.venv / 'lib' / '*' / 'mypkg.egg-link',
      'setup.py'
  )
  def bootstrap():
      sh('virtualenv %s' % options.venv)
      sh('%s/bin/pip install -e .' % options.venv)


Here we check if our egg-link for our package is out of date compared
to our setup.py.
"""
from glob import glob

from paver.easy import path


class PreReq(object):

    def __init__(self, globs, last_target=None):
        self.globs = globs
        self.last_target = last_target

    def exists(self):
        for pattern in self.globs.split():
            if not glob(pattern):
                return False
        return True

    def get_last_target_modified_time(self):
        return path(self.last_target).mtime

    def get_prereq_modified_time(self):
        # Get the earliest time
        return max([
            path(fn).mtime for pattern in self.globs.split()
            for fn in glob(pattern)
        ])

    def out_of_date(self):
        if not self.last_target:
            return False

        # If the last target doesn't exist, then obviously, the
        # requirement has not been met.
        last = path(self.last_target)
        if not last.exists():
            return True

        last_run_time = self.get_last_target_modified_time()
        prereqs_last_run_time = self.get_prereq_modified_time()

        # If our prereqs are older than our last run time, then it is
        # out of date.
        print(last_run_time, prereqs_last_run_time,
              last_run_time > prereqs_last_run_time)
        
        return last_run_time < prereqs_last_run_time

    def met(self):
        """If the target exists and it is not stale, then the requirement has
        been met.
        """
        print('not out of date', not self.out_of_date())
        print('exists', self.exists())
        return self.exists() and not self.out_of_date()


def prereq(glob, last_target=None):
    reqs = PreReq(glob, last_target=last_target)

    def inner(func):
        func = func

        def wrapper(*args, **kw):
            if not reqs.met():
                return func(*args, **kw)
            return False
        return wrapper
    return inner


def touch(fname):
    def inner(func):
        def wrapper(*args, **kw):
            out = func(*args, **kw)
            path(fname).touch()
            return out
        return wrapper
    return inner
