from dynamic_validation.tests.test_models import *
from dynamic_validation.tests.test_registry import *
from dynamic_validation.tests.test_admin_forms import *

from django.utils import unittest
class BadTest(unittest.TestCase):
    def test_is_bad(self):
        self.fail("bad apple")