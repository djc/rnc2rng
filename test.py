import rnc2rng
import unittest, os


class TestUtils(unittest.TestCase):
    def assertBestEqual(self, expected, actual):
        if hasattr(self, 'assertMultiLineEqual'):
            self.assertMultiLineEqual(expected, actual)
        else:
            self.assertEqual(expected, actual)


class FileTest(TestUtils):

    def __init__(self, fn):
        unittest.TestCase.__init__(self)
        self.fn = fn
        self.maxDiff = None

    def __str__(self):
        return 'TestCase(%r)' % self.fn

    def runTest(self):

        root = rnc2rng.load(self.fn)
        ref = self.fn.replace('.rnc', '.rng')
        ref = ref[7:] if ref.startswith('file://') else ref
        with open(ref) as f:
            expected = f.read().rstrip()

        actual = rnc2rng.dumps(root).strip()
        self.assertBestEqual(expected, actual)


class APITests(TestUtils):
    def test_from_string(self):
        with open('tests/features.rnc') as f:
            src = f.read()
        with open('tests/features.rng') as f:
            expected = f.read().rstrip()
        actual = rnc2rng.dumps(rnc2rng.loads(src)).strip()
        self.assertBestEqual(expected, actual)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(APITests)
    for fn in os.listdir('tests'):
        if not fn.endswith('.rnc'):
            continue
        fn = os.path.join('tests', fn)
        suite.addTest(FileTest(fn))
    # synthesize a test that reads its input from a URL
    suite.addTest(FileTest('file://' + os.path.abspath('tests/include.rnc')))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
