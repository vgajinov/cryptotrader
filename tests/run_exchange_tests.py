import unittest
from collections import deque


class Color:
    RED    = '\x1b[1;31m'
    GREEN  = '\x1b[1;32m'
    YELLOW = '\x1b[1;33m'
    BLUE   = '\x1b[1;34m'
    NONE   = '\033[0m'


def discover_tests(test_dir):
    """Uses unitest discover method to collect all tests in a given directory
    :return:  list of all discovered tests
    """
    loader = unittest.TestLoader()
    package_tests = loader.discover(start_dir=test_dir)
    test_suites = deque(package_tests)
    all_tests = []
    while test_suites:
        item = test_suites.pop()
        for obj in list(item):
            if type(obj) is unittest.TestSuite:
                test_suites.appendleft(obj)
            else:
                all_tests.append(obj)
    return all_tests


def create_test_dictionary(test_list):
    """Groups the tests by the TestCase they belong to
    :param test_list: a list of unittests
    :return: dict(test_case: test_list)
    """
    d = {}
    for tst in test_list:
        tst_type = type(tst)
        if 'test_exchanges' not in tst_type.__module__:
            continue
        if d.get(tst_type, None):
            d[tst_type].append(tst)
        else:
            d[tst_type] = [tst]
    return d


def run_tests(test_dict):
    """Runs the tests and applies report formatting
    :param test_dict: a dictionary of test grouped by the test case they belong to
    """
    for key, value in test_dict.items():
        print()
        print(f"{Color.YELLOW}{key.__module__}", f"{Color.BLUE}{key.__name__}{Color.NONE}")
        print('-' * 100)
        suite = unittest.TestSuite()
        suite.addTests(value)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
        print()


if __name__ == '__main__':
    tests = discover_tests('test_exchanges')
    test_dictionary = create_test_dictionary(tests)
    run_tests(test_dictionary)

