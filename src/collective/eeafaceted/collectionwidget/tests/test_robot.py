"""Robot suites of tests/robot, run with the layer of their file name.

ROBOT_PLONE_MAJOR selects the UI keywords (ui_plone6.robot): robotsuite passes the
ROBOT_* environment variables to the suites as robot variables.
The `plone4-bug` tag marks a scenario that failed on Plone 4.3 only (MIGRATION.md Known issues).
"""

from ..testing.layers import ACCEPTANCE
from importlib.metadata import version
from plone.testing import layered

import os
import robotsuite
import unittest


# suites needing an optional integration layer, e.g. {'test_facetednav.robot': ADDONS_ACCEPTANCE}
SUITE_LAYERS = {}


def test_suite():
    os.environ.setdefault(
        "ROBOT_PLONE_MAJOR", version("Products.CMFPlone").split(".")[0]
    )
    suite = unittest.TestSuite()
    robot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot")
    for name in sorted(os.listdir(robot_dir)):
        if name.startswith("test_") and name.endswith(".robot"):
            suite.addTests(
                [
                    layered(
                        robotsuite.RobotTestSuite(os.path.join("robot", name)),
                        layer=SUITE_LAYERS.get(name, ACCEPTANCE),
                    ),
                ]
            )
    return suite
