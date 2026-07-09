import sys
import importlib.abc
import importlib.util

class Loader(importlib.abc.Loader):

    def exec_module(self, module):
        module.msg = "Hello Import"

class Finder(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):

        if fullname == "demo":

            return importlib.util.spec_from_loader(
                fullname,
                Loader()
            )

sys.meta_path.insert(0, Finder())

import demo

print(demo.msg)