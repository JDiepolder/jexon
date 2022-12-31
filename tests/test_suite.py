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
    stdout, stderr = get_stdouterr_from_popen('ls')
    print(stdout)
    stdout, stderr = get_stdouterr_from_popen('ls ..')
    print(stdout)
    stdout, stderr = get_stdouterr_from_popen('ls ../jexon')
    print(stdout)
    _, stderr = get_stdouterr_from_popen(
        'python3 -m jexon.execute "tests/test_{}.json" "tests/output_{}.json" "tests/config.json"'.format(test_name, test_name))

    if stderr:
        print(stderr)
    
    with open("output_{}.json".format(test_name)) as f:
        output = json.load(f)

    with open("expected_{}.json".format(test_name)) as f:
        expected = json.load(f)
        
    return stderr, output, expected


class TestGeneric(unittest.TestCase):

    def test_flat(self):
        test_name = "flat"
        stderr, output, expected = run_and_load(test_name)
        self.assertEqual(stderr, '', "Test run {} failed.".format(test_name))
        self.assertEqual(output, expected, "Output is not as expected.")
        os.remove("output_{}.json".format(test_name))

    def test_flat_nested(self):
        test_name = "flat_nested"
        stderr, output, expected = run_and_load(test_name)
        self.assertEqual(stderr, '', "Test run {} failed.".format(test_name))
        self.assertEqual(output, expected, "Output is not as expected.")
        os.remove("output_{}.json".format(test_name))
