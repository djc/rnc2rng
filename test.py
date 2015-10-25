import rnc2rng
import unittest, os

class RNCTest(unittest.TestCase):

    def __init__(self, fn):
        unittest.TestCase.__init__(self)
        self.fn = fn
        self.maxDiff = None

    def __str__(self):
        return 'TestCase(%r)' % os.path.basename(self.fn)

    def runTest(self):

        with open(self.fn) as f:
            src = f.read()
        with open(self.fn.replace('.rnc', '.rng')) as f:
            expected = f.read().rstrip()

        actual = rnc2rng.dumps(rnc2rng.loads(src)).strip()
        self.assertMultiLineEqual(expected, actual)

def suite():
    suite = unittest.TestSuite()
    for fn in os.listdir('tests'):
        if not fn.endswith('.rnc'):
            continue
        fn = os.path.join('tests', fn)
        suite.addTest(RNCTest(fn))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
