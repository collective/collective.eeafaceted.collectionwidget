# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.interfaces import IWidgetDefaultValue
from collective.eeafaceted.collectionwidget.testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from collective.eeafaceted.collectionwidget.widgets.widget import ICollectionSchema
from DateTime import DateTime
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.widgets.storage import Criterion
from imio.helpers.cache import cleanRamCacheFor
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.annotation import IAnnotations
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.interface import Interface

import json
import lxml.html


COLLECTION_VOCABULARY = "collective.eeafaceted.collectionwidget.collectionvocabulary"


class BaseWidgetCase(IntegrationTestCase):
    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.folder = self.portal.folder
        self.category1 = api.content.create(
            id="category1", type="Folder", title="Category 1", container=self.folder
        )
        self.category2 = api.content.create(
            id="category2", type="Folder", title="Category 2", container=self.folder
        )
        self.collection1 = api.content.create(
            id="collection1",
            type="DashboardCollection",
            title="Collection 1",
            showNumberOfItems=True,
            query=[],
            sort_on="sortable_title",
            sort_reversed=False,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            container=self.category1,
        )
        self.collection2 = api.content.create(
            id="collection2",
            type="DashboardCollection",
            title="Collection 2",
            showNumberOfItems=True,
            query=[],
            sort_on="sortable_title",
            sort_reversed=False,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            container=self.category2,
        )
        subtyper = getMultiAdapter(
            (self.folder, self.request), name=u"faceted_subtyper"
        )
        subtyper.enable()


class TestWidget(BaseWidgetCase):
    """Test widget methods"""

    def _render(self, widget):
        """Render p_widget as an lxml tree, widget.default and categories are memoized on the request."""
        IAnnotations(self.request).pop("plone.memoize", None)
        return lxml.html.fromstring(widget())

    def test_widget_type(self):
        # registered as faceted widget, used by the 'c1' criterion of the faceted
        criteria = ICriteria(self.folder)
        self.assertEqual(CollectionWidget.widget_type, "collection-link")
        self.assertIs(criteria.widget(cid="c1"), CollectionWidget)
        self.assertIs(criteria.schema(cid="c1"), ICollectionSchema)

    def test_update(self):
        # fields 'index' and 'catalog' are removed from the edit form
        widget = CollectionWidget(
            self.folder, self.request, data=getCollectionLinkCriterion(self.folder)
        )
        widget.update()
        default_group = widget.groups[0]
        self.assertEqual(
            list(default_group.widgets.keys()),
            ["title", "vocabulary", "hidealloption", "default", "hide_category"],
        )
        self.assertNotIn("index", default_group.fields)
        self.assertNotIn("catalog", default_group.fields)

    def test_hide_category(self):
        data = Criterion()
        self.assertFalse(
            CollectionWidget(self.folder, self.request, data=data).hide_category
        )
        data.hide_category = True
        self.assertTrue(
            CollectionWidget(self.folder, self.request, data=data).hide_category
        )

    def test_get_category(self):
        data = dict(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        # collection outside a category folder does not have a category
        collection3 = api.content.create(
            id="collection3",
            type="DashboardCollection",
            title="Collection 3",
            showNumberOfItems=True,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            container=self.folder,
        )
        vocabulary = widget._generate_vocabulary()
        self.assertEqual(len(vocabulary), 3)  # 3 categories including '' (no category)
        self.assertEqual(len(vocabulary[""]["collections"]), 1)
        self.assertEqual(vocabulary[""]["collections"][0].token, collection3.UID())

    def test_generate_vocabulary(self):
        data = dict(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        vocabulary = widget._generate_vocabulary()
        self.assertEqual(len(vocabulary), 2)
        first_category, second_category = list(vocabulary.values())
        self.assertEqual(u"Category 1", first_category["term"].title)
        self.assertEqual(u"Category 2", second_category["term"].title)
        self.assertEqual(len(first_category["collections"]), 1)
        self.assertEqual(len(second_category["collections"]), 1)
        self.assertEqual(
            (
                first_category["collections"][0].token,
                first_category["collections"][0].title,
            ),
            (self.collection1.UID(), (self.collection1.Title(), "")),
        )
        self.assertEqual(
            (
                second_category["collections"][0].token,
                second_category["collections"][0].title,
            ),
            (self.collection2.UID(), (self.collection2.Title(), "")),
        )
        # if a category is private and not viewable by user
        # contained collections will not be displayed
        # make category1 folder not accessible by test_user_1_
        cat1 = self.portal.folder.category1
        cat1.manage_permission("View")
        cat1.reindexObjectSecurity()
        self.collection1.manage_permission("View", ("Authenticated",))
        self.collection1.reindexObjectSecurity()
        member = api.user.get_current()
        self.assertTrue(not member.has_permission("View", cat1))
        self.assertTrue(member.has_permission("View", self.collection1))
        # clean memoize for widget.categories,
        # it was memoized when calling _generate_vocabulary here above
        del IAnnotations(self.request)["plone.memoize"]
        # clean ram.cache for CollectionCategoryVocabulary
        cleanRamCacheFor(
            "collective.eeafaceted.collectionwidget.vocabulary."
            "CollectionCategoryVocabulary__call__"
        )
        vocabulary = widget._generate_vocabulary()
        # both collections appear in widget.vocabulary()
        self.assertEqual(
            [elt.token for elt in widget.vocabulary()],
            [self.collection1.UID(), self.collection2.UID()],
        )
        self.assertNotIn(
            u"Category 1", [c["term"].title for c in list(vocabulary.values())]
        )
        # with hide_category, every collection is listed without category,
        # even the one of the category the user can not see
        data = Criterion(vocabulary=COLLECTION_VOCABULARY, hide_category=True)
        widget = CollectionWidget(self.folder, self.request, data=data)
        vocabulary = widget._generate_vocabulary()
        self.assertEqual(list(vocabulary.keys()), [""])
        self.assertEqual(
            [term.token for term in vocabulary[""]["collections"]],
            [self.collection1.UID(), self.collection2.UID()],
        )

    def test_hidealloption(self):
        data = Criterion()
        data.hidealloption = u"0"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertFalse(widget.hidealloption)
        data.hidealloption = u"1"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertTrue(widget.hidealloption)

    def test_sortreversed(self):
        data = Criterion()
        data.sortreversed = u"0"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertFalse(widget.sortreversed)
        data.sortreversed = u"1"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertTrue(widget.sortreversed)

    def test_default_term_value(self):
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        data.sortreversed = u"0"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertEqual(
            widget.default_term_value, self.collection1.absolute_url_path()
        )
        data.sortreversed = u"1"
        widget = CollectionWidget(self.folder, self.request, data=data)
        self.assertEqual(
            widget.default_term_value, self.collection2.absolute_url_path()
        )

    def test_advanced_criteria(self):
        # we have an advanced criteria 'review_state' with name 'c2'
        widget = CollectionWidget(self.folder, self.request)
        self.assertEqual(len(widget.advanced_criteria), 3)
        self.assertEqual(
            widget.advanced_criteria,
            {u"c3": u"Creator", u"c2": u"review_state", u"c4": "created"},
        )

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
        self.assertEqual(
            json.loads(kept_criteria_as_json), {u"c3": [], u"c2": [], u"c4": []}
        )
        # ok, now update collection1 so it manage 'review_state'
        collection1.query = [
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["private"],
            }
        ]
        # now 'c2' will be hidden
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        self.assertEqual(
            json.loads(kept_criteria_as_json),
            {u"c3": [], u"c2": [u"private"], u"c4": []},
        )
        # but it is still kept when using collection2
        collection2 = self.folder.category2.collection2
        kept_criteria_as_json = widget.kept_criteria_as_json(collection2.UID())
        self.assertEqual(
            json.loads(kept_criteria_as_json), {u"c3": [], u"c2": [], u"c4": []}
        )

        # test case where value is a string, not a list
        collection1.query = [
            {"i": "Creator", "o": "plone.app.querystring.operation.string.currentUser"}
        ]
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        self.assertEqual(
            json.loads(kept_criteria_as_json),
            {u"c3": [u"test-user"], u"c2": [], u"c4": []},
        )

        # test case where value is a DateTime
        collection1.query = [
            {
                "i": "created",
                "o": "plone.app.querystring.operation.date.lessThan",
                "v": DateTime(2000, 1, 1),
            },
        ]
        kept_criteria_as_json = widget.kept_criteria_as_json(collection1.UID())
        self.assertEqual(json.loads(kept_criteria_as_json)["c4"][:10], u"2000-01-01")

    def test_default(self):
        # no default value selected
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget()
        self.assertEqual(widget.default, "")
        # a default value is selected, it will use adapter_default_value
        collection1UID = self.collection1.UID()
        widget.data.default = collection1UID
        # default is memoized, so clean it
        del IAnnotations(self.request)["plone.memoize"]
        widget()
        self.assertEqual(widget.default, collection1UID)
        # if the selected value is no more available, it falls back to first available element
        self.collection1.getParentNode().manage_delObjects(
            ids=[self.collection1.getId()]
        )
        del IAnnotations(self.request)["plone.memoize"]
        widget()
        self.assertEqual(widget.data.default, collection1UID)
        self.assertEqual(widget.default, self.collection2.UID())
        # if no fallback available, it will return None
        self.collection2.getParentNode().manage_delObjects(
            ids=[self.collection2.getId()]
        )
        del IAnnotations(self.request)["plone.memoize"]
        widget()
        self.assertEqual(widget.default, "")

    def test_count(self):
        data = Criterion()
        widget = CollectionWidget(self.folder, self.request, data=data)
        catalog = getToolByName(self.portal, "portal_catalog")
        brains = catalog(UID=self.collection1.UID())
        count_dico = widget.count(brains)
        # without vocabulary and sequence
        self.assertEqual(count_dico, {})
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget._generate_vocabulary()
        self.request.form["c1[]"] = self.collection1.UID()
        count_dico = widget.count(brains)
        # with vocabulary
        self.assertEqual(
            count_dico, {self.collection1.UID(): 8, self.collection2.UID(): 8}
        )
        # with sequence
        sequence = {u"": 1, self.collection1.UID(): 2}
        count_dico = widget.count(brains, sequence=sequence)
        self.assertEqual(count_dico, {u"": 1, self.collection1.UID(): 8})

    def test_query(self):
        self.collection1.query = [
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["private"],
            }
        ]
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        widget._generate_vocabulary()
        # no collection_uid
        query_dico = widget.query(form={data.__name__: ""})
        self.assertEqual(query_dico, {})
        # with collection_uid
        self.request.form["c0"] = self.collection1.UID()
        # make also getCurrentCollection happy
        self.request.form["c1[]"] = self.collection1.UID()
        query_dico = widget.query(self.request.form)
        # the sort_on paramter of the collection is taken into account
        self.assertTrue(self.collection1.sort_on == "sortable_title")
        self.assertTrue(self.collection1.sort_reversed is False)
        self.assertEqual(
            query_dico,
            {"review_state": {"query": ["private"]}, "sort_on": "sortable_title"},
        )
        # if sort_reversed is True, it is kept in the query
        self.collection1.setSort_reversed(True)
        query_dico = widget.query(form={data.__name__: widget.vocabulary()[0].token})
        self.assertEqual(
            query_dico,
            {
                "review_state": {"query": ["private"]},
                "sort_on": "sortable_title",
                "sort_order": "descending",
            },
        )
        # if we receive a value for a SortingCriterion,
        # then the sort defined on the collection will not be used
        # here c0 is a SortingCriterion
        self.request.form["c0[]"] = "created"
        query_dico = widget.query(form={data.__name__: widget.vocabulary()[0].token})
        self.assertEqual(query_dico, {"review_state": {"query": ["private"]}})

    def test_call(self):
        data = Criterion(vocabulary=COLLECTION_VOCABULARY)
        widget = CollectionWidget(self.folder, self.request, data=data)
        html = widget()
        self.assertTrue(self.collection1.Title() in html)
        self.assertTrue(self.collection1.UID() in html)

        # with the criterion of the faceted
        uid1 = self.collection1.UID()
        uid2 = self.collection2.UID()
        criterion = getCollectionLinkCriterion(self.folder)
        widget = CollectionWidget(self.folder, self.request, data=criterion)
        tree = self._render(widget)
        # option 'All', selected as there is no default, then the collections grouped by category
        self.assertEqual(
            [li.get("id") for li in tree.xpath("//li")],
            ["c1all", "c1" + uid1, "c1" + uid2],
        )
        all_option = tree.xpath("//li")[0]
        self.assertEqual(
            all_option.get("class"), "no-category-tag faceted-tag-selected"
        )
        self.assertEqual(
            json.loads(all_option.get("data-kept-criteria")),
            {"c2": [], "c3": [], "c4": []},
        )
        self.assertEqual(
            [
                div.text
                for div in tree.xpath('//div[@class="category"]/div[@class="title"]')
            ],
            ["Category 1", "Category 2"],
        )
        # a default collection unselects 'All'
        criterion.default = uid1
        tree = self._render(widget)
        self.assertEqual(tree.xpath("//li")[0].get("class"), "no-category-tag")
        # hidealloption
        criterion.hidealloption = True
        tree = self._render(widget)
        self.assertEqual(
            [li.get("id") for li in tree.xpath("//li")], ["c1" + uid1, "c1" + uid2]
        )
        # hide_category
        criterion.hide_category = True
        tree = self._render(widget)
        self.assertEqual(tree.xpath('//div[@class="title"]'), [])
        self.assertEqual(
            [li.get("id") for li in tree.xpath("//li")], ["c1" + uid1, "c1" + uid2]
        )
        # no collection: nothing rendered, except in the faceted widgets edit form, with option 'All'
        for collection in (self.collection1, self.collection2):
            collection.enabled = False
            collection.reindexObject(idxs=["enabled"])
        IAnnotations(self.request).pop("plone.memoize", None)
        self.assertEqual(widget().strip(), "")
        self.request.set("URL0", self.folder.absolute_url() + "/@@faceted_widgets")
        tree = self._render(widget)
        self.assertEqual([li.get("id") for li in tree.xpath("//li")], ["c1all"])

    def test_render_category(self):
        widget = CollectionWidget(
            self.folder, self.request, data=getCollectionLinkCriterion(self.folder)
        )
        term = widget.categories.getTermByToken(self.category1.UID())
        div = lxml.html.fromstring(widget.render_category(term))
        self.assertEqual((div.get("class"), div.text), ("title", "Category 1"))

    def test_render_term(self):
        uid1 = self.collection1.UID()
        uid2 = self.collection2.UID()
        self.collection1.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["Folder"],
            }
        ]
        self.collection2.showNumberOfItems = False
        criterion = getCollectionLinkCriterion(self.folder)
        criterion.default = uid1
        widget = CollectionWidget(self.folder, self.request, data=criterion)
        widget._initialize_widget()  # done by widget.__call__ before rendering the terms
        terms = dict((term.token, term) for term in widget.vocabulary())
        # term in a category, selected by default, with the number of items
        li = lxml.html.fromstring(widget.render_term(terms[uid1], self.category1.UID()))
        self.assertEqual(li.get("id"), "c1" + uid1)
        self.assertEqual(li.get("class"), "category1-collection1 faceted-tag-selected")
        self.assertEqual((li.get("value"), li.get("title")), (uid1, "Collection 1"))
        self.assertEqual(
            json.loads(li.get("data-kept-criteria")), {"c2": [], "c3": [], "c4": []}
        )
        self.assertEqual(li.xpath("a/@href"), ["javascript:;"])
        self.assertEqual(
            li.xpath('a/span[@class="term-label"]/text()'), ["Collection 1"]
        )
        self.assertEqual(li.xpath('a//span[@class="term-count"]/text()'), ["4"])
        # term without category, number of items not shown
        li = lxml.html.fromstring(widget.render_term(terms[uid2], ""))
        self.assertEqual(li.get("class"), "category2-collection2 no-category-tag")
        self.assertEqual(li.xpath('a//span[@class="term-count"]'), [])
        # collection in a faceted sub-folder: link to that folder
        getMultiAdapter(
            (self.category1, self.request), name=u"faceted_subtyper"
        ).enable()
        terms = dict((term.token, term) for term in widget.vocabulary())
        li = lxml.html.fromstring(widget.render_term(terms[uid1], self.category1.UID()))
        self.assertEqual(
            li.xpath("a/@href"),
            ["{0}?no_redirect=1#c1={1}".format(self.category1.absolute_url(), uid1)],
        )


class DefaultValue(object):
    def __init__(self, context, request, widget):
        self.value = context.category1.collection1


class TestWidgetWithDefaultValueAdapter(BaseWidgetCase):
    def test_adapter_default_value(self):
        widget = CollectionWidget(self.folder, self.request, data={})
        self.assertEqual(widget.adapter_default_value, self.collection1)

    def setUp(self):
        super(TestWidgetWithDefaultValueAdapter, self).setUp()
        sm = getGlobalSiteManager()
        sm.registerAdapter(
            factory=DefaultValue,
            required=(Interface, Interface, Interface),
            provided=IWidgetDefaultValue,
        )

    def tearDown(self):
        sm = getGlobalSiteManager()
        sm.unregisterAdapter(
            factory=DefaultValue,
            required=(Interface, Interface, Interface),
            provided=IWidgetDefaultValue,
        )
        super(TestWidgetWithDefaultValueAdapter, self).tearDown()
