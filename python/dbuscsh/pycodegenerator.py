__author__ = 'ilia'

import os
import os.path as path

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class Generator(object):

    def __init__(self, classname, filename):
        self._filename = filename
        self._classname= classname

    def add_method(self, methodname):
        pass

    def add_property(self):
        pass

    def add_constuctor(self):
        pass

    def add_header(self):
        pass

    def add_footer(self):
        pass

class PyGenerator(Generator):
    def __init__(self, classname, filename):
        super(PyGenerator, self).__init__(classname=classname, filename=filename)
        if not path.exists(path.dirname(filename)):
            os.makedirs(path.dirname(filename), 0o755)

        with open(self._filename, 'w') as f:
            pass

    @overrides(Generator)
    def add_method(self):
        pass

    @overrides(Generator)
    def add_header(self):
        with open(self._filename, 'w') as f:
            text = '''class %s (%s):
            \tpass''' % (self._classname, 'object')
            f.write(text)

    @overrides(Generator)
    def add_footer(self):
        pass


