import rnc2rng
import unittest, os
import sys
if sys.version_info[0] < 3:
    from urllib import pathname2url, url2pathname
    from urlparse import urljoin, urlparse
else:
    from urllib.parse import urljoin, urlparse
    from urllib.request import pathname2url, url2pathname


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
        if ref.startswith('file:'):
            parse_result = urlparse(ref)
            ref = url2pathname(parse_result.path)
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
    url_test_path = os.path.abspath('tests/include.rnc')
    suite.addTest(FileTest(urljoin('file:', pathname2url(url_test_path))))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
