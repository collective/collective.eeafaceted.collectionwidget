# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.adapters import DefaultValue
from collective.eeafaceted.collectionwidget.adapters import KeptCriteria
from collective.eeafaceted.collectionwidget.interfaces import IKeptCriteria
from collective.eeafaceted.collectionwidget.interfaces import IWidgetDefaultValue
from collective.eeafaceted.collectionwidget.tests.test_widget import BaseWidgetCase
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from DateTime import DateTime
from plone.dexterity.browser.add import DefaultAddView
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter


class TestDefaultValue(BaseWidgetCase):
    def test_registration(self):
        widget = CollectionWidget(
            self.folder, self.request, data=getCollectionLinkCriterion(self.folder)
        )
        widget._initialize_widget()
        self.assertIsInstance(
            getMultiAdapter((self.folder, self.request, widget), IWidgetDefaultValue),
            DefaultValue,
        )
        # registered for the widget only: CMFCore's ++add++ traverser takes an unnamed
        # (container, request, type info) adapter as the add view of the type
        fti = self.portal.portal_types.DashboardCollection
        self.assertIsNone(
            queryMultiAdapter((self.folder, self.request, fti), IWidgetDefaultValue)
        )
        self.assertIsInstance(
            self.folder.restrictedTraverse("++add++DashboardCollection"),
            DefaultAddView,
        )


class TestKeptCriteria(BaseWidgetCase):
    """More cases in test_widget.test_kept_criteria_as_json."""

    def test_compute(self):
        widget = CollectionWidget(
            self.folder, self.request, data=getCollectionLinkCriterion(self.folder)
        )
        adapter = getMultiAdapter((self.folder, widget), IKeptCriteria)
        self.assertIsInstance(adapter, KeptCriteria)
        # the 'All' option keeps every advanced criterion
        self.assertEqual(adapter.compute("all"), {"c2": [], "c3": [], "c4": []})
        # unknown collection
        self.assertEqual(adapter.compute("unknown_uid"), {})
        # a DateIndex queried with a list of dates (between) keeps the criterion, without values
        self.collection1.query = [
            {
                "i": "created",
                "o": "plone.app.querystring.operation.date.between",
                "v": ["2000/01/01", "2001/01/01"],
            }
        ]
        self.assertEqual(
            adapter.compute(self.collection1.UID()), {"c2": [], "c3": [], "c4": []}
        )
        # a single text value is wrapped in a list (unicode on Python 2)
        self.collection1.query = [
            {
                "i": "Creator",
                "o": "plone.app.querystring.operation.string.is",
                "v": "test-user",
            }
        ]
        self.assertEqual(
            adapter.compute(self.collection1.UID()),
            {"c2": [], "c3": ["test-user"], "c4": []},
        )
        # a single date is returned as is (widget.kept_criteria_as_json converts it)
        self.collection1.query = [
            {
                "i": "created",
                "o": "plone.app.querystring.operation.date.lessThan",
                "v": DateTime("2000/01/01"),
            }
        ]
        self.assertEqual(
            adapter.compute(self.collection1.UID()),
            {"c2": [], "c3": [], "c4": DateTime("2000/01/01")},
        )
