# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase


class TestDashboardCollection(IntegrationTestCase):
    """Test the DashboardCollection content type."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.portal
        )

    def test_displayCatalogQuery(self):
        """This will display a readable version of the catalog query."""
        self.dashboardcollection.query = [
            {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Folder', ]},
        ]
        self.assertEquals(self.dashboardcollection.displayCatalogQuery(),
                          {'portal_type': {'query': ['Folder']}})
