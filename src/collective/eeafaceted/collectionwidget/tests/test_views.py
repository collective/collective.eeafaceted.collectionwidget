# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.browser.views import QueryBuilder
from collective.eeafaceted.collectionwidget.tests.test_widget import BaseWidgetCase
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.interfaces import ICriteria
from zope.component import getMultiAdapter


class TestViews(BaseWidgetCase):
    """Test the views."""

    def test_FacetedDashboardView(self):
        subtyper = getMultiAdapter(
            (self.category1, self.request), name=u"faceted_subtyper"
        )
        subtyper.enable()
        # enabling a faceted will redirect to it, so, cancel this
        self.request.RESPONSE.status = 200

        # when default in self.folder, not redirected already at the right place
        view = getMultiAdapter(
            (self.folder, self.request), name=u"facetednavigation_view"
        )
        crit = getCollectionLinkCriterion(self.folder)
        crit.default = self.collection2.UID()
        ret = view()
        self.assertIn("Base collections", ret)
        self.assertEqual(self.request.RESPONSE.status, 200)

        # now set default on a collection of the subfolder
        crit.default = self.collection1.UID()

        # not redirected if we are on folder/folder_contents or folder/configure_faceted.html
        # or it is no more possible to access the folder actions, always redirected to subfolder...
        self.request["URL"] = self.folder.absolute_url() + "/folder_contents"
        ret = view()
        self.assertIn("Base collections", ret)
        self.assertEqual(self.request.RESPONSE.status, 200)
        folderURL = self.folder.absolute_url()
        self.request["URL"] = folderURL
        self.request["HTTP_REFERER"] = (
            self.folder.absolute_url() + "/configure_faceted.html"
        )
        ret = view()
        self.assertIn("Base collections", ret)
        self.assertEqual(self.request.RESPONSE.status, 200)

        # we are redirected to the subfolder if accessing directly folder
        self.request["URL"] = folderURL
        self.request["HTTP_REFERER"] = folderURL
        ret = view()
        self.assertFalse(ret)
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), self.category1.absolute_url()
        )

        # not redirected when a collection is selected (c1[] in the request)
        self.request.RESPONSE.setStatus(200)
        self.request.form["c1[]"] = self.collection1.UID()
        self.assertIn("Base collections", view())
        self.assertEqual(self.request.RESPONSE.status, 200)
        del self.request.form["c1[]"]
        # redirected without HTTP_REFERER (Zope returns '' for a missing HTTP_ header)
        del self.request.other["HTTP_REFERER"]
        self.assertEqual(self.request["HTTP_REFERER"], "")
        self.assertEqual(view(), "")
        self.assertEqual(self.request.RESPONSE.status, 302)
        # not redirected with no_redirect=1 (links of the collection vocabulary)
        self.request.RESPONSE.setStatus(200)
        self.request.form["no_redirect"] = "1"
        self.assertIn("Base collections", view())
        self.assertEqual(self.request.RESPONSE.status, 200)
        # nor when the faceted has no collection widget
        ICriteria(self.folder).delete(crit.getId())
        self.assertIn("faceted-form", view())
        self.assertEqual(self.request.RESPONSE.status, 200)


class TestRenderTermView(BaseWidgetCase):
    def test_display_number_of_items(self):
        view = getMultiAdapter(
            (self.collection1, self.request), name="render_collection_widget_term"
        )
        self.assertTrue(view.display_number_of_items())
        self.collection1.showNumberOfItems = False
        self.assertFalse(view.display_number_of_items())
        # always displayed for another kind of collection
        view = getMultiAdapter(
            (self.folder, self.request), name="render_collection_widget_term"
        )
        self.assertTrue(view.display_number_of_items())

    def test_number_of_items(self):
        self.collection1.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["Folder"],
            }
        ]
        view = getMultiAdapter(
            (self.collection1, self.request), name="render_collection_widget_term"
        )
        self.assertEqual(view.number_of_items(), 4)
        self.assertEqual(view.number_of_items(init=True), 4)
        # count computed later (by the JS) when compute_count_on_init is False
        view.compute_count_on_init = False
        self.assertEqual(view.number_of_items(init=True), "...")
        self.assertEqual(view.number_of_items(), 4)


class TestQueryBuilder(BaseWidgetCase):
    def _querybuilder(self):
        """The querybuilderresults view of our browser layer, it caches its results."""
        return getMultiAdapter((self.folder, self.request), name="querybuilderresults")

    def test__makequery(self):
        """No "path" added to the query (the catalog ignores the {'query': ''} added by the
        original, so the results do not differ: only the registration and results are tested)."""
        self.assertIsInstance(self._querybuilder(), QueryBuilder)
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["DashboardCollection"],
            }
        ]
        # brains
        results = self._querybuilder()(
            query=query, sort_on="sortable_title", brains=True
        )
        self.assertEqual(
            [b.Title for b in results],
            ["Collection 1", "Collection 2", "Creator", "Review state"],
        )
        # content listing, sort order
        results = self._querybuilder()(
            query=query, sort_on="sortable_title", sort_order="reverse"
        )
        self.assertEqual(
            [item.Title() for item in results],
            ["Review state", "Creator", "Collection 2", "Collection 1"],
        )
        # batch
        results = self._querybuilder()(
            query=query, sort_on="sortable_title", batch=True, b_start=1, b_size=2
        )
        self.assertEqual(results.sequence_length, 4)
        self.assertEqual(
            [item.Title() for item in results], ["Collection 2", "Creator"]
        )
        # limit
        results = self._querybuilder()(
            query=query, sort_on="sortable_title", limit=2, brains=True
        )
        self.assertEqual(results.actual_result_count, 2)
        # custom_query overrides the query
        results = self._querybuilder()(
            query=query, brains=True, custom_query={"getId": "collection2"}
        )
        self.assertEqual([b.getId for b in results], ["collection2"])
        # no valid index
        unknown = [
            {
                "i": "unknown_index",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["x"],
            }
        ]
        self.assertEqual(self._querybuilder()(query=unknown, brains=True), [])
        self.assertEqual(len(self._querybuilder()(query=unknown)), 0)
