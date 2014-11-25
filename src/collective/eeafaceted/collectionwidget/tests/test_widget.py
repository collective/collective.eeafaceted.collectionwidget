# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from plone import api

from ..testing.testcase import IntegrationTestCase


class TestVocabulary(IntegrationTestCase):
    """Test computation of vocabulary"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal.folder

    def test_categoryvocabulary(self):
        from collective.eeafaceted.collectionwidget.vocabulary import (
            CollectionCategoryVocabularyFactory
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
        vocabulary = CollectionCategoryVocabularyFactory(self.folder)
        self.assertEquals(len(vocabulary), 2)
        self.assertTrue('category1' in vocabulary)
        self.assertEquals('Category 1', vocabulary.getTerm('category1').title)
        self.assertTrue('category2' in vocabulary)
        self.assertEquals('Category 2', vocabulary.getTerm('category2').title)

    def test_collectionvocabulary(self):
        from collective.eeafaceted.collectionwidget.vocabulary import (
            CollectionVocabularyFactory
        )
        """There should be collections
        """
        c1 = api.content.create(
            id='collection1',
            type='Collection',
            title='Collection 1',
            container=self.folder
        )
        c2 = api.content.create(
            id='collection2',
            type='Collection',
            title='Collection 2',
            container=self.folder
        )
        vocabulary = CollectionVocabularyFactory(self.folder)
        self.assertEquals(len(vocabulary), 2)
        self.assertTrue(c1.UID() in vocabulary)
        self.assertEquals(
            'Collection 1',
            vocabulary.getTerm(c1.UID()).title
        )
        self.assertTrue(c2.UID() in vocabulary)
        self.assertEquals(
            'Collection 2',
            vocabulary.getTerm(c2.UID()).title
        )
