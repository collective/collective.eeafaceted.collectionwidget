# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from plone import api
from eea.facetednavigation.interfaces import ICriteria
from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget.vocabulary import CollectionCategoryVocabularyFactory
from collective.eeafaceted.collectionwidget.vocabulary import CollectionVocabularyFactory
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget


class TestVocabulary(IntegrationTestCase):
    """Test computation of vocabulary"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.folder = self.portal.folder
        subtyper = getMultiAdapter(
            (self.folder, self.request), name=u'faceted_subtyper'
        )
        subtyper.enable()

    def test_categoryvocabulary(self):
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
        self.assertEquals('Category 1', vocabulary.getTermByToken(self.folder.category1.UID()).title)
        self.assertEquals('Category 2', vocabulary.getTermByToken(self.folder.category2.UID()).title)

    def test_collectionvocabulary(self):
        """ """
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

        self.assertTrue(c1.UID() in [term.token for term in vocabulary])
        self.assertTrue(c2.UID() in [term.token for term in vocabulary])
        self.assertEquals([(u'Collection 1', ''), (u'Collection 2', '')],
                          [term.title for term in vocabulary])

    def test_with_sub_faceted(self):
        """Test behaviour of the vocabulary when we have subfolders
           with activated faceted navigation."""
        # add collection to self.folder
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

        # create a subfolder, add collections into it
        api.content.create(
            id='subfolder',
            type='Folder',
            title='Subfolder',
            container=self.folder
        )
        c3 = api.content.create(
            id='collection3',
            type='Collection',
            title='Collection 3',
            container=self.folder.subfolder
        )
        c4 = api.content.create(
            id='collection4',
            type='Collection',
            title='Collection 4',
            container=self.folder.subfolder
        )

        # for now, faceted navigation is not enabled on subfolder,
        # it behaves like a normal category

        vocabulary = CollectionVocabularyFactory(self.folder)
        folderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder)
        subfolderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder.subfolder)
        self.assertTrue(folderCatVocabulary.by_token.keys() ==
                        subfolderCatVocabulary.by_token.keys())
        # redirect_to is not filled
        self.assertFalse(vocabulary.getTermByToken(c1.UID()).title[1])
        self.assertFalse(vocabulary.getTermByToken(c2.UID()).title[1])
        self.assertFalse(vocabulary.getTermByToken(c3.UID()).title[1])
        self.assertFalse(vocabulary.getTermByToken(c4.UID()).title[1])

        # now enable faceted navigation for subfolder
        subtyper = getMultiAdapter((self.folder.subfolder, self.request),
                                   name=u'faceted_subtyper')
        subtyper.enable()
        # change the CollectionWidget id to "c44" so we are sure that
        # the generated link is the one to this widget
        self.assertEquals(self.folder.subfolder.__annotations__['FacetedCriteria'][1].widget,
                          CollectionWidget.widget_type)
        self.folder.subfolder.__annotations__['FacetedCriteria'][1].__name__ = u'c44'
        vocabulary = CollectionVocabularyFactory(self.folder)
        folderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder)
        subfolderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder.subfolder)
        self.assertTrue(folderCatVocabulary.by_token.keys() ==
                        subfolderCatVocabulary.by_token.keys())
        # as we are getting the vocabulary on self.folder,
        # redirect_to is filled for collections of subfolder
        # while generating links to specific sub faceted, a 'no_redirect' is added
        # so the user is not redirected to the faceted using the default
        self.assertFalse(vocabulary.getTermByToken(c1.UID()).title[1])
        self.assertFalse(vocabulary.getTermByToken(c2.UID()).title[1])
        self.assertEquals(vocabulary.getTermByToken(c3.UID()).title[1],
                          '{0}?no_redirect=1#c44={1}'.format(self.folder.subfolder.absolute_url(),
                                                             c3.UID())
                          )
        self.assertEquals(vocabulary.getTermByToken(c4.UID()).title[1],
                          '{0}?no_redirect=1#c44={1}'.format(self.folder.subfolder.absolute_url(),
                                                             c4.UID())
                          )

        # if we get vocabulary from subfolder, it works the other way round
        # but moreover, we have a no_redirect=1 that avoid to redirect if we
        # are sending the user to the root folder of the faceted navigation
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        folderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder)
        subfolderCatVocabulary = CollectionCategoryVocabularyFactory(self.folder.subfolder)
        self.assertTrue(folderCatVocabulary.by_token.keys() ==
                        subfolderCatVocabulary.by_token.keys())
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}'.format(self.folder.absolute_url(),
                                                            c1.UID())
                          )
        self.assertEquals(vocabulary.getTermByToken(c2.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}'.format(self.folder.absolute_url(),
                                                            c2.UID())
                          )
        self.assertFalse(vocabulary.getTermByToken(c3.UID()).title[1])
        self.assertFalse(vocabulary.getTermByToken(c4.UID()).title[1])

        # test the generated link when having a faceted using a sorting index reversed or not
        data = {'default': u'effective(reverse)'}
        sortingCriterionId = ICriteria(self.folder).add('sorting', 'top', **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c4=effective&reversed=on'.format(self.folder.absolute_url(),
                                                                                     c1.UID()))
        data = {'default': u'effective'}
        ICriteria(self.folder).edit(sortingCriterionId, **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c4=effective'.format(self.folder.absolute_url(),
                                                                         c1.UID()))

        # test that other default values are kept also, add a 'resultsperpage' widget
        data = {'default': u'20'}
        ICriteria(self.folder).add('resultsperpage', 'top', **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c4=effective&c5=20'.format(self.folder.absolute_url(),
                                                                               c1.UID()))
