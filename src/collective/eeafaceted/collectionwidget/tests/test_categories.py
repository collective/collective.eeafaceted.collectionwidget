# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.eeafaceted.collectionwidget.testing import IntegrationTestCase


class TestCategories(IntegrationTestCase):
    """Test computation of collection categories"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal.folder

    def test_no_categories(self):
        from collective.eeafaceted.collectionwidget.categories import (
            CategoriesFromFolder
        )
        """There should be no categories
        when the folder does not hold any folders.
        """
        categories = CategoriesFromFolder(self.folder).values
        self.assertFalse(categories)
