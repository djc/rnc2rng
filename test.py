from __future__ import print_function

import rnc2rng
import unittest, glob, random


class RNCTest(unittest.TestCase):
    def assertBestEqual(self, expected, actual):
        if hasattr(self, 'assertMultiLineEqual'):
            self.assertMultiLineEqual(expected, actual)
        else:
            self.assertEqual(expected, actual)

    def test_load(self):
        """Test all RNC files in the test file directory with `load()`."""
        for source_file in glob.iglob('tests/*.rnc'):
            print('Testing %r...' % source_file)
            with open(source_file) as fd:
                root = rnc2rng.load(fd)

            with open(source_file.replace('.rnc', '.rng')) as fd:
                expected = fd.read().strip()

            actual = rnc2rng.dumps(root).strip()
            self.assertBestEqual(expected, actual)

    def test_loads(self):
        """We should be able to parse a file without giving a filename"""
        # Pick a random source file
        source_file = random.choice(glob.glob('tests/*.rnc'))
        expected_file = source_file.replace('.rnc', '.rng')

        # Load the code and convert it. Everything should behave normally.
        with open(source_file, 'r') as fd:
            root = rnc2rng.loads(fd.read())

        with open(expected_file, 'r') as fd:
            expected = fd.read().strip()

        actual = rnc2rng.dumps(root).strip()
        self.assertBestEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
