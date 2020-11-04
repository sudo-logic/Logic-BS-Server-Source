import sys
import traceback
import some


class TracePrints(object):
    def __init__(self):
        self.stdout = sys.stdout

    def write(self, s):
        self.stdout.write(repr(s))
        self.stdout.write('\n')
        if s != '\n':
            traceback.print_stack(file=self.stdout)
    def flush(self):
        pass


if some.debug:
    sys.stdout = TracePrints()
