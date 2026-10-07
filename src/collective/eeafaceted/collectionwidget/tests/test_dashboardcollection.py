# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase
from DateTime import DateTime
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides


class TestDashboardCollection(IntegrationTestCase):
    """Test the DashboardCollection content type."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.dashboardcollection = api.content.create(
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.portal,
        )

    def test_displayCatalogQuery(self):
        """This will display a readable version of the catalog query."""
        self.dashboardcollection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": [
                    "Folder",
                ],
            },
        ]
        self.assertEqual(
            self.dashboardcollection.displayCatalogQuery(),
            {"portal_type": {"query": ["Folder"]}},
        )

    def test_brains_results(self):
        """Catalog brains of the query, sorted on creation date (the collection sort_on is not used)."""
        self.portal.folder.setCreationDate(DateTime("2010/01/01"))
        self.portal.folder.reindexObject(idxs=["created"])
        self.portal.folder2.setCreationDate(DateTime("2000/01/01"))
        self.portal.folder2.reindexObject(idxs=["created"])
        self.dashboardcollection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["Folder"],
            },
        ]
        self.dashboardcollection.sort_on = "sortable_title"
        self.assertEqual(
            [b.getId for b in self.dashboardcollection.brains_results()],
            ["folder2", "folder"],
        )

    def test_results(self):
        """Unlike a Collection, results are not limited to the navigation root."""
        folder = self.portal.folder
        alsoProvides(folder, INavigationRoot)
        dc = api.content.create(
            id="dc2",
            type="DashboardCollection",
            title="Dashboard collection 2",
            container=folder,
            query=[
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": ["Folder"],
                }
            ],
            sort_on="id",
            sort_reversed=False,
        )
        self.assertEqual(
            [b.getId for b in dc.results(batch=False, brains=True)],
            ["folder", "folder2"],
        )
        # batched content listing by default, sort_reversed and custom_query are used
        dc.sort_reversed = True
        results = dc.results(b_size=1)
        self.assertEqual(results.sequence_length, 2)
        self.assertEqual([item.getId() for item in results], ["folder2"])
        self.assertEqual(
            [
                b.getId
                for b in dc.results(brains=True, custom_query={"getId": "folder"})
            ],
            ["folder"],
        )
