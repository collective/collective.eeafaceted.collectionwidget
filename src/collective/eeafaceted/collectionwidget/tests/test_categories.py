# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from plone import api

from ..testing.testcase import IntegrationTestCase


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

    def test_categories(self):
        from collective.eeafaceted.collectionwidget.categories import (
            CategoriesFromFolder
        )
        """There should be categories
        """
        api.content.create(
            id='category1',
            type='Folder',
            title='Category 1',
            container=self.folder
        )
        api.content.create(
            id='category2',
            type='Folder',
            title='Category 2',
            container=self.folder
        )
        categories = CategoriesFromFolder(self.folder).values
        self.assertEquals(len(categories), 2)
        self.assertEquals(['Category 1', 'Category 2'],
                          [c[1].Title() for c in categories])

    def test_categories_only_from_folder(self):
        from collective.eeafaceted.collectionwidget.categories import (
            CategoriesFromFolder
        )
        """Only folders are categories
        """
        api.content.create(
            type='Folder',
            title='category1',
            container=self.folder
        )
        api.content.create(
            type='Folder',
            title='category2',
            container=self.folder
        )
        api.content.create(
            type='Document',
            title='not a category',
            container=self.folder
        )
        categories = CategoriesFromFolder(self.folder).values
        self.assertEquals(len(categories), 2)

    def test_categories_ordered(self):
        from collective.eeafaceted.collectionwidget.categories import (
            CategoriesFromFolder
        )
        """categories should be ordered as the folders in the dashboard
        """
        api.content.create(
            id='category1',
            type='Folder',
            title='Category 1',
            container=self.folder
        )
        api.content.create(
            id='category2',
            type='Folder',
            title='Category 2',
            container=self.folder
        )
        categories = CategoriesFromFolder(self.folder).values
        self.assertEquals('Category 1', categories[0][1].Title())
        self.assertEquals('Category 2', categories[1][1].Title())
        self.folder.moveObjectsUp(['category2'])
        categories = CategoriesFromFolder(self.folder).values
        self.assertEquals('Category 2', categories[0][1].Title())
        self.assertEquals('Category 1', categories[1][1].Title())

    def test_no_subCategorie(self):
        from collective.eeafaceted.collectionwidget.categories import (
            CategoriesFromFolder
        )
        """subfolders are not categories
        """
        category1 = api.content.create(
            type='Folder',
            title='category1',
            container=self.folder
        )
        api.content.create(
            type='Folder',
            title='category3',
            container=category1
        )
        api.content.create(
            type='Folder',
            title='category2',
            container=self.folder
        )
        categories = CategoriesFromFolder(self.folder).values
        self.assertEquals(len(categories), 2)
