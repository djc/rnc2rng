import rnc2rng
import unittest, os

class RNCTest(unittest.TestCase):

    def __init__(self, fn):
        unittest.TestCase.__init__(self)
        self.fn = fn
        self.maxDiff = None

    def __str__(self):
        return 'TestCase(%r)' % os.path.basename(self.fn)

    def assertBestEqual(self, expected, actual):
        if hasattr(self, 'assertMultiLineEqual'):
            self.assertMultiLineEqual(expected, actual)
        else:
            self.assertEqual(expected, actual)

    def runTest(self):

        with open(self.fn) as f:
            root = rnc2rng.load(f)
        with open(self.fn.replace('.rnc', '.rng')) as f:
            expected = f.read().rstrip()

        actual = rnc2rng.dumps(root).strip()
        self.assertBestEqual(expected, actual)

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
