import os
import unittest

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover(os.path.dirname(__file__))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
