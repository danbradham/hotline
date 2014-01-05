import glob
import os
import sys
from unittest import TestSuite, defaultTestLoader

sys.path.append('.')
TEST_PATH = "tests"


def module_path(file_path):
    '''Convert a file path to a dotted module path.'''

    return '.'.join(os.path.split(file_path.split(".")[0]))


def get_suites():
    '''Returns test suites for all test modules in TEST_PATH'''

    paths = [module_path(f) for f in glob.glob(TEST_PATH + "/test_*.py")]
    print paths
    mods = [__import__(path) for path in paths]
    print mods
    test_from_module = defaultTestLoader.loadTestsFromModule
    return [test_from_module(m) for m in mods]

if __name__ == "__main__":
    test_suite = TestSuite()
    suites = get_suites()
    print suites
    test_suite.addTests(suites)
    print test_suite
