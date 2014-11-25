# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from plone import api

from ..testing.testcase import IntegrationTestCase


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.collectionwidget into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.eeafaceted.collectionwidget is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.eeafaceted.collectionwidget'))

    def test_uninstall(self):
        """Test if collective.eeafaceted.collectionwidget is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.eeafaceted.collectionwidget'])
        self.assertFalse(self.installer.isProductInstalled('collective.eeafaceted.collectionwidget'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveEeafacetedCollectionwidgetLayer is registered."""
        from collective.eeafaceted.collectionwidget.interfaces import ICollectiveEeafacetedCollectionwidgetLayer
        from plone.browserlayer import utils
        self.assertIn(ICollectiveEeafacetedCollectionwidgetLayer, utils.registered_layers())
