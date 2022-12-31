import unittest
import json
import subprocess
import os


def get_stdouterr_from_popen(cmd):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()
    proc.wait()
    return (str(stdout.decode("utf-8")), str(stderr.decode("utf-8")))

def run_and_load(test_name):
    _, stderr = get_stdouterr_from_popen(
        'python3 -m jexon.execute "tests/test_{}.json" "tests/output_{}.json" "tests/config.json"'.format(test_name, test_name))

    if stderr:
        print(stderr)
    
    with open("tests/output_{}.json".format(test_name)) as f:
        output = json.load(f)

    with open("tests/expected_{}.json".format(test_name)) as f:
        expected = json.load(f)
    
    return stderr, output, expected


class TestGeneric(unittest.TestCase):

    def run_test(self, test_name):
        stderr, output, expected = run_and_load(test_name)
        self.assertEqual(stderr, '', "Test run {} failed.".format(test_name))
        self.assertEqual(output, expected, "Output is not as expected.")
        os.remove("tests/output_{}.json".format(test_name))

    def test_flat(self):
        self.run_test("flat")

    def test_flat_nested(self):
        self.run_test("flat_nested")
        
    def test_string(self):
        self.run_test("string")

    def test_flat_modules(self):
        self.run_test("flat_modules")

    def test_nested(self):
        self.run_test("nested")
