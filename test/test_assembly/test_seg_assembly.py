import unittest

from assembly2.seg6_segment import segments


class SegmentTest(unittest.TestCase):
    NUMBER_OF_FILES: int = 40

    def test_files(self):
        self.assertTrue('TS02' in segments)
        self.assertTrue('TS01' in segments)
        self.assertFalse('EB0EB' in segments)
        self.assertEqual(self.NUMBER_OF_FILES, len(segments), 'Update number of files in SegmentTest')


if __name__ == '__main__':
    unittest.main()
