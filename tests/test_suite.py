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
    def __init__(self, test_name):
        super(TestCase, self).__init__("test_generic")
        self.test_name = test_name

    def setUp(self):
        print("\n> test setup: " + self.test_name)
        pass

    def test_generic(self):
        stdout, stderr = get_stdouterr_from_popen(
            'ls ..'.format(test_name=self.test_name))
            # 'cd .. && ls && python -m jexon.execute "tests/test_{test_name}.json" "tests/output_{test_name}.json" "tests/config.json"'.format(test_name=self.test_name))
        
        print(stdout)
        
        if stderr:
            print(stderr)
        self.assertEqual(
            stderr, '', "Test run {} failed.".format(self.test_name))

        with open("output_{}.json".format(self.test_name)) as f:
            self.assertEqual(
                f.closed, False, "Output file for {} could not be opened.".format(self.test_name))
            output = json.load(f)

        with open("expected_{}.json".format(self.test_name)) as f:
            self.assertEqual(
                f.closed, False, "Expected file for {} could not be opened.".format(self.test_name))
            expected = json.load(f)

        self.assertEqual(output, expected, "Output is not as expected.")

        os.remove("output_{}.json".format(self.test_name))

    def tearDown(self):
        print("\n< test teardown: " + self.test_name)
        pass


def suite():
    suite = unittest.TestSuite()
    testFiles = glob.glob('test_*.json')
    for testFile in testFiles:
        print(testFile)
        suite.addTest(TestCase(testFile[5:-5]))
    return suite


if __name__ == '__main__':
    print("##############################################################################")
    print("# Running jexon Test Suite")
    print("##############################################################################")
    runner = unittest.TextTestRunner()
    runner.run(suite())
