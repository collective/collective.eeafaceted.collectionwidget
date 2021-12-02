# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.interfaces import NoCollectionWidgetDefinedException
from collective.eeafaceted.collectionwidget.interfaces import NoFacetedViewDefinedException
from collective.eeafaceted.collectionwidget.tests.test_widget import BaseWidgetCase
from collective.eeafaceted.collectionwidget.utils import _get_criterion
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.widgets.sorting.widget import Widget as SortingWidget
from zope.annotation import IAnnotations


class TestUtils(BaseWidgetCase):
    """Test the utils."""

    def test__get_criterion(self):
        """This method is used by getCollectionLinkCriterion to get
           the current CollectionWidget but may be used to get any
           kind of criterion."""
        # get the collection widget
        self.assertEqual(_get_criterion(self.folder, CollectionWidget.widget_type).widget,
                         CollectionWidget.widget_type)
        # get the sorting widget
        self.assertEqual(_get_criterion(self.folder, SortingWidget.widget_type).widget,
                         SortingWidget.widget_type)

    def test_getCollectionLinkCriterion(self):
        """This method will return the Collection-link widget defined on a folder if ever."""
        # self.folder is faceted enabled
        self.assertEqual(getCollectionLinkCriterion(self.folder).widget,
                         CollectionWidget.widget_type)
        # remove the criterion then try to get it again
        ICriteria(self.folder).delete(getCollectionLinkCriterion(self.folder).getId())
        with self.assertRaises(NoCollectionWidgetDefinedException):
            getCollectionLinkCriterion(self.folder)
        # trying to get collection-link widget on a folder that is not
        # faceted enabled will raise a NoFacetedViewDefinedException
        folder3_id = self.portal.invokeFactory('Folder', 'folder3', title='Folder3')
        folder3 = getattr(self.portal, folder3_id)
        self.assertRaises(NoFacetedViewDefinedException, getCollectionLinkCriterion, folder3)

    def test_getCurrentCollection(self):
        """Returns the Collection currently used by the CollectionWidget in a faceted."""
        dashcoll = self.collection1

        # current collection is get with collectionLink id in the REQUEST, not set for now
        criterion = getCollectionLinkCriterion(self.folder)
        criterion_name = '{0}[]'.format(criterion.__name__)
        request = self.portal.REQUEST
        self.assertFalse(criterion_name in request)
        self.assertIsNone(getCurrentCollection(self.folder))

        # set a correct collection in the REQUEST
        request.form[criterion_name] = dashcoll.UID()
        self.assertEqual(getCurrentCollection(self.folder), dashcoll)

        # it works also with 'facetedQuery' build in the REQUEST when generating
        # a template on a dashboard
        del request.form[criterion_name]
        # getcurrentCollection is cached, remove infos in request annotation
        cache_key = 'collectionwidget-utils-getCurrentCollection-{0}'.format(self.folder.UID())
        del IAnnotations(request)[cache_key]
        self.assertIsNone(getCurrentCollection(self.folder))
        request.form['facetedQuery'] = '{{"c3":["20"],"b_start":["0"],"{0}":"{1}"}}'.format(
            criterion.__name__, dashcoll.UID())
        self.assertEqual(getCurrentCollection(self.folder), dashcoll)

    def test_updateDefaultCollectionFor(self):
        """This method will define the default collection used by the collection-link
           widget defined in a faceted enabled folder."""
        # get the collection-link and check that it has no default
        criterion = getCollectionLinkCriterion(self.folder)
        self.assertFalse(criterion.default)
        # right, do things correctly, add a DashboardCollection and use it as default
        dashcoll_id = self.folder.invokeFactory('DashboardCollection', 'dashcoll', title='Dashboard Collection')
        dashcoll = getattr(self.folder, dashcoll_id)
        dashcoll.reindexObject()
        _updateDefaultCollectionFor(self.folder, dashcoll.UID())
        self.assertEqual(criterion.default, dashcoll.UID())

        # calling it on a non faceted enabled folder will raise a NoFacetedViewDefinedException
        nonfacetedfolder_id = self.portal.invokeFactory('Folder', 'notnacetedfolder', title='Non Faceted Folder')
        nonfacetedfolder = getattr(self.portal, nonfacetedfolder_id)
        nonfacetedfolder.reindexObject()
        self.assertRaises(NoFacetedViewDefinedException, _updateDefaultCollectionFor, nonfacetedfolder, 'anUID')
