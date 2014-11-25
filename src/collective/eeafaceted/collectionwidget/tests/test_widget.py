# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from plone import api

from ..testing.testcase import IntegrationTestCase
from eea.facetednavigation.widgets.storage import Criterion


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


class TestWidget(IntegrationTestCase):
    """Test widget methods"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal.folder
        self.category1 = api.content.create(
            id='category1',
            type='Folder',
            title='Category 1',
            container=self.folder
        )
        self.category2 = api.content.create(
            id='category2',
            type='Folder',
            title='Category 2',
            container=self.folder
        )
        self.collection1 = api.content.create(
            id='collection1',
            type='Collection',
            title='Collection 1',
            container=self.category1
        )
        self.collection2 = api.content.create(
            id='collection2',
            type='Collection',
            title='Collection 2',
            container=self.category2
        )

    def test_get_category(self):
        request = self.layer['request']
        from ..widgets.collectionlink.widget import Widget
        widget = Widget(self.folder, request, data={})
        category = widget._get_category('')
        self.assertEquals(category, u'')
        category = widget._get_category(self.collection2.UID())
        self.assertEquals(category, 'category2')
        # content outside a category folder does not have a category
        collection3 = api.content.create(
            id='collection3',
            type='Collection',
            title='Collection 3',
            container=self.folder
        )
        category = widget._get_category(collection3.UID())
        self.assertEquals(category, u'')

    def test_generate_vocabulary(self):
        request = self.layer['request']
        from ..widgets.collectionlink.widget import Widget
        data = dict(vocabulary='collective.eeafaceted.collectionwidget.collectionvocabulary')
        widget = Widget(self.folder, request, data=data)
        vocabulary = widget._generate_vocabulary()
        self.assertEquals(len(vocabulary), 2)
        self.assertTrue('category1' in vocabulary)
        self.assertTrue('category2' in vocabulary)
        self.assertEquals(vocabulary['category1'], [(self.collection1.UID(), self.collection1.Title())])
        self.assertEquals(vocabulary['category2'], [(self.collection2.UID(), self.collection2.Title())])

    def test_hidealloption(self):
        request = self.layer['request']
        from ..widgets.collectionlink.widget import Widget
        data = Criterion()
        data.hidealloption = u'0'
        widget = Widget(self.folder, request, data=data)
        self.assertFalse(widget.hidealloption)
        data.hidealloption = u'1'
        widget = Widget(self.folder, request, data=data)
        self.assertTrue(widget.hidealloption)

    def test_sortreversed(self):
        request = self.layer['request']
        from ..widgets.collectionlink.widget import Widget
        data = Criterion()
        data.sortreversed = u'0'
        widget = Widget(self.folder, request, data=data)
        self.assertFalse(widget.sortreversed)
        data.sortreversed = u'1'
        widget = Widget(self.folder, request, data=data)
        self.assertTrue(widget.sortreversed)
