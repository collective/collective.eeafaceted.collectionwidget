# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
import json
from zope.annotation import IAnnotations
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.interface import Interface
from plone import api
from Products.CMFCore.utils import getToolByName

from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget.interfaces import IWidgetDefaultValue
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from eea.facetednavigation.widgets.storage import Criterion

COLLECTION_VOCABULARY = (
    'collective.eeafaceted.collectionwidget.collectionvocabulary'
)


class BaseWidgetCase(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
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
        subtyper = getMultiAdapter(
            (self.folder, self.request), name=u'faceted_subtyper'
        )
        subtyper.enable()


class TestWidget(BaseWidgetCase):
    """Test widget methods"""

    def test_get_category(self):
        data = dict(
            vocabulary=COLLECTION_VOCABULARY
        )
        widget = CollectionWidget(self.folder, self.request, data=data)
        # collection outside a category folder does not have a category
        collection3 = api.content.create(
            id='collection3',
            type='Collection',
            title='Collection 3',
            container=self.folder
        )
        vocabulary = widget._generate_vocabulary()
        self.assertEquals(len(vocabulary), 3)  # 3 categories including '' (no category)
        self.assertEquals(len(vocabulary['']['collections']), 1)
        self.assertEquals(vocabulary['']['collections'][0].token, collection3.UID())

    def test_generate_vocabulary(self):
        data = dict(
            vocabulary=COLLECTION_VOCABULARY
        )
        widget = CollectionWidget(self.folder, self.request, data=data)
        vocabulary = widget._generate_vocabulary()
        self.assertEquals(len(vocabulary), 2)
        first_category, second_category = vocabulary.values()
        self.assertEquals(u'Category 1', first_category['term'].title)
        self.assertEquals(u'Category 2', second_category['term'].title)
        self.assertEquals(len(first_category['collections']), 1)
        self.assertEquals(len(second_category['collections']), 1)
        self.assertEquals(
            (first_category['collections'][0].token, first_category['collections'][0].title),
            (self.collection1.UID(), (self.collection1.Title(), ''))
        )
        self.assertEquals(
            (second_category['collections'][0].token, second_category['collections'][0].title),
            (self.collection2.UID(), (self.collection2.Title(), ''))
        )
        # if a category is private and not viewable by user
        # contained collections will not be displayed
        # make category1 folder not accessible by test_user_1_
        cat1 = self.portal.folder.category1
        cat1.manage_permission('View')
        cat1.reindexObjectSecurity()
        self.collection1.manage_permission('View', ('Authenticated', ))
        member = self.portal.portal_membership.getAuthenticatedMember()
        self.assertTrue(not member.has_permission('View', cat1))
        self.assertTrue(member.has_permission('View', self.collection1))
        # clean memoize for widget.categories,
        # it was memoized when calling _generate_vocabulary here above
        del IAnnotations(self.request)['plone.memoize']
        vocabulary = widget._generate_vocabulary()
        self.assertNotIn(u'Category 1', [c['term'].title for c in vocabulary.values()])

    def test_hidealloption(self):
        data = Criterion()
        data.hidealloption = u'0'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertFalse(widget.hidealloption)
        data.hidealloption = u'1'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertTrue(widget.hidealloption)

    def test_sortreversed(self):
        data = Criterion()
        data.sortreversed = u'0'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertFalse(widget.sortreversed)
        data.sortreversed = u'1'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertTrue(widget.sortreversed)

    def test_default_term_value(self):
        data = Criterion(
            vocabulary=COLLECTION_VOCABULARY
        )
        data.sortreversed = u'0'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertEquals(widget.default_term_value, self.collection1)
        data.sortreversed = u'1'
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertEquals(widget.default_term_value, self.collection2)

    def test_advanced_criteria(self):
        # we have an advanced criteria 'review_state' with name 'c2'
        widget = CollectionWidget(self.folder, self.request)
        self.assertEquals(len(widget.advanced_criteria), 2)
        self.assertEquals(widget.advanced_criteria, {u'c3': u'Creator', u'c2': u'review_state'})

    def test_kept_criteria_as_json(self):
        widget = CollectionWidget(self.folder, self.request)
        # kept criteria are criteria in the 'advanced' section managed by the
        # faceted that are not by a given collection UID
        # by default, advanced widget 'c2' managing review_state is kept
        # for collection1 because collection does not manage this index
        collection1 = self.folder.category1.collection1
        # response is in JSON format
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        # response is valid JSON
        self.assertEquals(json._default_decoder.decode(kept_criteria_as_json),
                          {u'c3': [], u'c2': []})
        # ok, now update collection1 so it manage 'review_state'
        collection1.query = [{'i': 'review_state',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['private']}]
        # now 'c2' will be hidden
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        self.assertEquals(json._default_decoder.decode(kept_criteria_as_json),
                          {u'c3': [], u'c2': [u'private']})
        # but it is still kept when using collection2
        collection2 = self.folder.category2.collection2
        kept_criteria_as_json = widget.kept_criteria_as_json(collection2.UID())
        self.assertEquals(json._default_decoder.decode(kept_criteria_as_json),
                          {u'c3': [], u'c2': []})

        # test case where value is a string, not a list
        collection1.query = [{'i': 'Creator',
                              'o': 'plone.app.querystring.operation.string.currentUser'
                              }]
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        self.assertEquals(json._default_decoder.decode(kept_criteria_as_json),
                          {u'c3': [u'test-user'], u'c2': []})

    def test_default(self):
        # no default value selected
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget()
        self.assertEquals(widget.default, None)
        # a default value is selected, it will use adapter_default_value
        collection1UID = self.collection1.UID()
        widget.data.default = collection1UID
        # default is memoized, so clean it
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(widget.default, collection1UID)
        # if the selected value is no more available, it falls back to first available element
        self.collection1.getParentNode().manage_delObjects(ids=[self.collection1.getId()])
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(widget.data.default, collection1UID)
        self.assertEquals(widget.default, self.collection2.UID())
        # if no fallback available, it will return None
        self.collection2.getParentNode().manage_delObjects(ids=[self.collection2.getId()])
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(widget.default, None)

    def test_default_subfaceted(self):
        """If default is in a subfolder with a faceted defined on it,
           user will be redirected to this subfolder then the default will be displayed."""
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        # create a subfolder, add collections into it
        # and activate the faceted navigation
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
        subtyper = getMultiAdapter((self.folder.subfolder, self.request),
                                   name=u'faceted_subtyper')
        subtyper.enable()
        # enabling a faceted will redirect to it, so, cancel this
        self.request.RESPONSE.status = 200

        # when default in self.folder, not redirected already at the right place
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget.data.default = self.collection1.UID()
        widget()
        self.assertEquals(self.request.RESPONSE.status, 200)

        # now set default on a collection of the subfolder
        widget.data.default = c3.UID()

        # not redirected if we are on folder/folder_contents or folder/configure_faceted.html
        # or it is no more possible to access the folder actions, always redirected to subfolder...
        self.request['URL'] = self.folder.absolute_url() + '/folder_contents'
        # call to 'default' is memoized, so clean it
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(self.request.RESPONSE.status, 200)
        folderURL = self.folder.absolute_url()
        self.request['URL'] = folderURL
        self.request['HTTP_REFERER'] = self.folder.absolute_url() + '/configure_faceted.html'
        # call to 'default' is memoized, so clean it
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(self.request.RESPONSE.status, 200)

        # we are redirected to the subfolder if accessing directly folder
        self.request['URL'] = folderURL
        self.request['HTTP_REFERER'] = folderURL
        # call to 'default' is memoized, so clean it
        del IAnnotations(self.request)['plone.memoize']
        widget()
        self.assertEquals(self.request.RESPONSE.status, 302)
        self.assertEquals(self.request.RESPONSE.getHeader('location'), self.folder.subfolder.absolute_url())

    def test_count(self):
        data = Criterion()
        widget = CollectionWidget(self.folder, self.request, data=data)
        catalog = getToolByName(self.portal, 'portal_catalog')
        brains = catalog(UID=self.collection1.UID())
        count_dico = widget.count(brains)
        # without vocabulary and sequence
        self.assertEquals(count_dico, {})
        data = Criterion(
            vocabulary=COLLECTION_VOCABULARY
        )
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget._generate_vocabulary()
        count_dico = widget.count(brains)
        # with vocabulary
        self.assertEquals(
            count_dico,
            {self.collection1.UID(): 8, self.collection2.UID(): 8}
        )
        # with sequence
        sequence = {u'': 1, self.collection1.UID(): 2}
        count_dico = widget.count(brains, sequence=sequence)
        self.assertEquals(
            count_dico,
            {u'': 1, self.collection1.UID(): 8}
        )

    def test_query(self):
        self.collection1.query = [{'i': 'review_state',
                                   'o': 'plone.app.querystring.operation.selection.is',
                                   'v': ['private']}]
        data = Criterion(
            vocabulary=COLLECTION_VOCABULARY
        )
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget._generate_vocabulary()
        # no collection_uid
        query_dico = widget.query(form={data.__name__: ''})
        self.assertEquals(query_dico, {})
        # with collection_uid
        query_dico = widget.query(form={data.__name__: widget.vocabulary()[0].token})
        # the sort_on paramter of the collection is taken into account
        self.assertTrue(self.collection1.getSort_on() == 'sortable_title')
        self.assertTrue(self.collection1.getSort_reversed() is False)
        self.assertEquals(query_dico, {'review_state': {'query': ['private']},
                                       'sort_on': 'sortable_title'})
        # if sort_reversed is True, it is kept in the query
        self.collection1.setSort_reversed(True)
        query_dico = widget.query(form={data.__name__: widget.vocabulary()[0].token})
        self.assertEquals(query_dico, {'review_state': {'query': ['private']},
                                       'sort_on': 'sortable_title',
                                       'sort_order': 'descending'})
        # if we receive a value for a SortingCriterion,
        # then the sort defined on the collection will not be used
        # here c0 is a SortingCriterion
        self.request.form['c0[]'] = 'created'
        query_dico = widget.query(form={data.__name__: widget.vocabulary()[0].token})
        self.assertEquals(query_dico, {'review_state': {'query': ['private']}})

    def test_call(self):
        data = Criterion(
            vocabulary=COLLECTION_VOCABULARY
        )
        widget = CollectionWidget(self.folder, self.request, data=data)
        html = widget()
        self.assertTrue(self.collection1.Title() in html)
        self.assertTrue(self.collection1.UID() in html)


class DefaultValue(object):
    def __init__(self, context, request, widget):
        self.value = context.category1.collection1


class TestWidgetWithDefaultValueAdapter(BaseWidgetCase):

    def test_adapter_default_value(self):
        widget = CollectionWidget(self.folder, self.request, data={})
        self.assertEquals(widget.adapter_default_value, self.collection1)

    def setUp(self):
        super(TestWidgetWithDefaultValueAdapter, self).setUp()
        sm = getGlobalSiteManager()
        sm.registerAdapter(
            factory=DefaultValue,
            required=(Interface, Interface, Interface),
            provided=IWidgetDefaultValue
        )

    def tearDown(self):
        sm = getGlobalSiteManager()
        sm.unregisterAdapter(
            factory=DefaultValue,
            required=(Interface, Interface, Interface),
            provided=IWidgetDefaultValue
        )
        super(TestWidgetWithDefaultValueAdapter, self).tearDown()
