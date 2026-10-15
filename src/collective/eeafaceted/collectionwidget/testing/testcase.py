from .layers import FUNCTIONAL
from .layers import INTEGRATION

import unittest


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super().setUp()
        self.portal = self.layer["portal"]


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
