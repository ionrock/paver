from mock import patch

from paver import tasks
from paver.easy import path
from paver.make import prereq, touch, PreReq


class IsStalePreReq(PreReq):

    def get_last_target_modified_time(self):
        prereq_time = self.get_prereq_modified_time()
        return prereq_time - 10


class IsFreshPreReq(PreReq):

    def get_last_target_modified_time(self):
        prereq_time = self.get_prereq_modified_time()
        return prereq_time + 10


class TestPrereq(object):
    fname = path('prereq_test.txt')
    last_fname = path('prereq_result.txt')

    def cleanup(self):
        self.fname.remove()
        self.last_fname.remove()

    def setup(self):
        self.cleanup()

    def teardown(self):
        self.cleanup()

    def test_prereq_exists(self):

        @tasks.task
        @prereq(self.fname)
        def doit():
            return True

        self.fname.touch()
        result = doit()
        assert not result
        assert doit.called

    def test_prereq_not_exists(self):

        @tasks.task
        @prereq(self.fname)
        def doit():
            return True

        result = doit()
        assert result
        assert doit.called

    def test_prereq_result_not_exist(self):
        @tasks.task
        @prereq(self.fname, self.last_fname)
        def doit():
            return True

        self.fname.touch()
        result = doit()
        assert result

    @patch('paver.make.PreReq', IsStalePreReq)
    def test_prereq_result_exist_is_stale(self):
        @tasks.task
        @prereq(self.fname, self.last_fname)
        def doit():
            return True

        self.fname.touch()
        self.last_fname.touch()

        result = doit()
        assert result

    @patch('paver.make.PreReq', IsFreshPreReq)
    def test_prereq_result_exist_is_fresh(self):
        @tasks.task
        @prereq(self.fname, self.last_fname)
        def doit():
            return True

        self.fname.touch()
        self.last_fname.touch()

        result = doit()
        assert not result


class TestTouchDecorator(object):

    fname = path(__file__).dirname() / 'touch_test.txt'

    def cleanup(self):
        if self.fname.exists():
            self.fname.remove()

    def setup(self):
        self.cleanup()

    def teardown(self):
        self.cleanup()

    def test_touch(self):

        @tasks.task
        @touch(self.fname)
        def doit():
            return True

        doit()

        assert self.fname.exists()
