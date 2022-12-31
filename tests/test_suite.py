import unittest
import json
import subprocess
import os
import glob


def get_stdouterr_from_popen(cmd):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()
    proc.wait()
    return (str(stdout.decode("utf-8")), str(stderr.decode("utf-8")))


class TestCase(unittest.TestCase):
    def __init__(self):
        super(TestGeneric, self).__init__("test_generic")

    def setUp(self):
        self.test_files = glob.glob('test_*.json')
        pass

    def test_generic(self):
        for test_file in self.test_files:

            test_name = test_file[5:-5]

            _, stderr = get_stdouterr_from_popen(
                'cd .. && python3 -m jexon.execute "tests/test_{}.json" "tests/output_{}.json" "tests/config.json"'.format(test_name))

            if stderr:
                print(stderr)
            self.assertEqual(
                stderr, '', "Test run {} failed.".format(test_name))

            with open("output_{}.json".format(test_name)) as f:
                self.assertEqual(
                    f.closed, False, "Output file for {} could not be opened.".format(test_name))
                output = json.load(f)

            with open("expected_{}.json".format(test_name)) as f:
                self.assertEqual(
                    f.closed, False, "Expected file for {} could not be opened.".format(test_name))
                expected = json.load(f)

            self.assertEqual(output, expected, "Output is not as expected.")

            os.remove("output_{}.json".format(test_name))

    def tearDown(self):
        pass
