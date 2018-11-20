# -*- coding: utf-8 -*-

from collective.behavior.talcondition.interfaces import ITALConditionable
from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget.vocabulary import CollectionCategoryVocabularyFactory
from collective.eeafaceted.collectionwidget.vocabulary import CollectionVocabularyFactory
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from eea.facetednavigation.interfaces import ICriteria
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory


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
            type='DashboardCollection',
            title='Collection 1',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        c2 = api.content.create(
            id='collection2',
            type='DashboardCollection',
            title='Collection 2',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        vocabulary = CollectionVocabularyFactory(self.folder)
        self.assertEquals(len(vocabulary), 2)

        self.assertTrue(c1.UID() in [term.token for term in vocabulary])
        self.assertTrue(c2.UID() in [term.token for term in vocabulary])
        self.assertEquals([(u'Collection 1', ''), (u'Collection 2', '')],
                          [term.title for term in vocabulary])

        # disabled DashboardCollection are not returned
        c2.enabled = False
        c2.reindexObject(idxs=['enabled'])
        vocabulary = CollectionVocabularyFactory(self.folder)
        self.assertEquals([(u'Collection 1', '')],
                          [term.title for term in vocabulary])

    def test_with_sub_faceted(self):
        """Test behaviour of the vocabulary when we have subfolders
           with activated faceted navigation."""
        # add collection to self.folder
        c1 = api.content.create(
            id='collection1',
            type='DashboardCollection',
            title='Collection 1',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        c2 = api.content.create(
            id='collection2',
            type='DashboardCollection',
            title='Collection 2',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
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
            type='DashboardCollection',
            title='Collection 3',
            container=self.folder.subfolder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        c4 = api.content.create(
            id='collection4',
            type='DashboardCollection',
            title='Collection 4',
            container=self.folder.subfolder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
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
        collection_widget = ICriteria(self.folder.subfolder).get('c1')
        self.assertEquals(collection_widget.widget,
                          CollectionWidget.widget_type)
        collection_widget.__name__ = u'c44'
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
        sortingCriterionId = ICriteria(self.folder).add('sorting', 'bottom', **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c5=effective&reversed=on'.format(self.folder.absolute_url(),
                                                                                     c1.UID()))
        data = {'default': u'effective'}
        ICriteria(self.folder).edit(sortingCriterionId, **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c5=effective'.format(self.folder.absolute_url(),
                                                                         c1.UID()))

        # test that other default values are kept also, add a 'resultsperpage' widget
        data = {'default': u'20'}
        ICriteria(self.folder).add('resultsperpage', 'bottom', **data)
        vocabulary = CollectionVocabularyFactory(self.folder.subfolder)
        self.assertEquals(vocabulary.getTermByToken(c1.UID()).title[1],
                          '{0}?no_redirect=1#c1={1}&c5=effective&c6=20'.format(self.folder.absolute_url(),
                                                                               c1.UID()))

    def test_conditionawarecollectionvocabulary(self):
        """This vocabulary is condition aware, it means
           that it will take into account condition defined in the
           'tal_condition' field added by ITALConditionable."""
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        # add on non Manager user
        api.user.create(
            username='user_not_manager',
            password='user_not_manager',
            email="imio@dashboard.org",
            roles=['Member'])
        self.assertTrue(ITALConditionable.providedBy(self.dashboardcollection))
        factory = queryUtility(IVocabularyFactory, u'collective.eeafaceted.collectionwidget.collectionvocabulary')
        # for now, no condition defined on the collection so it is in the vocabulary
        self.assertEqual(self.dashboardcollection.tal_condition, u'')
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)
        # now define a condition and by pass for Manager
        self.dashboardcollection.tal_condition = u'python:False'
        self.dashboardcollection.roles_bypassing_talcondition = [u"Manager"]
        notify(ObjectModifiedEvent(self.dashboardcollection))
        # No more listed except for Manager
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)
        login(self.portal, 'user_not_manager')
        # cache is user aware
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)
        # Now, desactivate bypass for manager
        login(self.portal, TEST_USER_NAME)
        self.dashboardcollection.roles_bypassing_talcondition = []
        # ObjectModified event on DashboardCollection invalidate the vocabulary caching
        notify(ObjectModifiedEvent(self.dashboardcollection))
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)
        # If condition is True, it is listed
        self.dashboardcollection.tal_condition = u'python:True'
        notify(ObjectModifiedEvent(self.dashboardcollection))
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)

    def test_cachedcollectionvocabulary(self):
        """This vocabulary is cached by and is invalidated when :
           - user changed;
           - a dashboardcollection is added/removed/edited/transition triggered;
           - faceted container."""
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[],
        )
        # add on non Manager user
        api.user.create(
            username='user_not_manager',
            password='user_not_manager',
            email="imio@dashboard.org",
            roles=['Member'])
        factory = queryUtility(IVocabularyFactory, u'collective.eeafaceted.collectionwidget.cachedcollectionvocabulary')
        # now define a condition and by pass for Manager
        self.dashboardcollection.tal_condition = u'python:False'
        self.dashboardcollection.roles_bypassing_talcondition = [u"Manager"]
        notify(ObjectModifiedEvent(self.dashboardcollection))
        # No more listed except for Manager
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)
        login(self.portal, 'user_not_manager')
        # cache is user aware
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)
        # Now, desactivate bypass for manager
        login(self.portal, TEST_USER_NAME)
        self.dashboardcollection.roles_bypassing_talcondition = []
        # ObjectModified event on DashboardCollection invalidate the vocabulary caching
        notify(ObjectModifiedEvent(self.dashboardcollection))
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)

        # cache invalidated when new DashboardCollection added
        self.dashboardcollection2 = api.content.create(
            id='dc2',
            type='DashboardCollection',
            title='Dashboard collection 2',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[]
        )
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection2.title in [term.title[0] for term in vocab._terms])

        # cache invalidated when DashboardCollection deleted
        api.content.delete(self.dashboardcollection2)
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection2.title in [term.title[0] for term in vocab._terms])
