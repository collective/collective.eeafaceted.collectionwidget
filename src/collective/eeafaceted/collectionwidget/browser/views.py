# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.content.dashboardcollection import IDashboardCollection
from collective.eeafaceted.collectionwidget.interfaces import NoCollectionWidgetDefinedException
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from imio.helpers.content import uuidToObject
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring import queryparser
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from plone.app.querystring.querybuilder import logger
from plone.app.querystring.querybuilder import QueryBuilder as OriginalQueryBuilder
from plone.batching import Batch
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getUtilitiesFor


class RenderCategoryView(BrowserView):

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url()

    def _get_category_template(self):
        '''Base method that returns the ViewPageTemplate to
           use to display the category.
           Made to be overrided, returns a ViewPageTemplate or None.'''
        return None

    def __call__(self, widget):
        self.widget = widget
        category_template = self._get_category_template()
        return category_template and category_template(self) or self.index()


class RenderTermView(BrowserView):

    compute_count_on_init = True

    def display_number_of_items(self):
        """Display number of items in the collection."""
        if not IDashboardCollection.providedBy(self.context):
            return True
        return self.context.showNumberOfItems

    def number_of_items(self, init=False):
        """Return the number of items in the collection."""
        if init and not self.compute_count_on_init:
            return "..."
        else:
            return len(self.context.results(
                batch=False, brains=True, custom_query={"sort_on": None}))

    def __call__(self, term, category, widget):
        self.term = term
        self.category = category
        self.widget = widget
        return self.index()


class FacetedDashboardView(FacetedContainerView):
    """ Facetednavigation view, managing default collection widget redirection """

    @property
    def _criteriaHolder(self):
        """Return the criteria holder, the container where the criteria are stored,
           as criteria is get thru an adapter, it could be stored elsewhere
           than on the context."""
        return self.context

    def __call__(self):
        criteria_holder = self._criteriaHolder
        criterion = None
        try:
            criterion = getCollectionLinkCriterion(criteria_holder)
        except NoCollectionWidgetDefinedException:
            pass
        if criterion:
            # if we have the collection UID in the REQUEST, return self.index()
            # so we avoid the portal_catalog search for collection
            collectionUID = self.context.REQUEST.form.get('{0}[]'.format(criterion.__name__))
            if collectionUID or not criterion.default:
                return self.index()
            if not self.request['HTTP_REFERER'].endswith('configure_faceted.html') and \
               not self.request['URL'].endswith('folder_contents') and \
               not self.request.get('no_redirect', '0') == '1':
                collection = uuidToObject(criterion.default, unrestricted=True)
                if collection:
                    container = collection.aq_inner.aq_parent
                    if not container == criteria_holder and \
                       IFacetedNavigable.providedBy(container):
                        self.request.RESPONSE.redirect(container.absolute_url())
                        return ''
        return self.index()


class QueryBuilder(OriginalQueryBuilder):
    """ """

    def _makequery(self, query=None, batch=False, b_start=0, b_size=30,
                   sort_on=None, sort_order=None, limit=0, brains=False,
                   custom_query=None):
        """Overrided to avoid added "path" index."""
        parsedquery = queryparser.parseFormquery(
            self.context, query, sort_on, sort_order)

        index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
        for name, modifier in index_modifiers:
            if name in parsedquery:
                new_name, query = modifier(parsedquery[name])
                parsedquery[name] = query
                # if a new index name has been returned, we need to replace
                # the native ones
                if name != new_name:
                    del parsedquery[name]
                    parsedquery[new_name] = query

        # Check for valid indexes
        catalog = getToolByName(self.context, 'portal_catalog')
        valid_indexes = [index for index in parsedquery
                         if index in catalog.indexes()]

        # We'll ignore any invalid index, but will return an empty set if none
        # of the indexes are valid.
        if not valid_indexes:
            logger.warning(
                "Using empty query because there are no valid indexes used.")
            parsedquery = {}

        if not parsedquery:
            if brains:
                return []
            else:
                return IContentListing([])

        if batch:
            parsedquery['b_start'] = b_start
            parsedquery['b_size'] = b_size
        elif limit:
            parsedquery['sort_limit'] = limit

        # Begin changes, comment "path" arbitrary added
        # if 'path' not in parsedquery:
        #     parsedquery['path'] = {'query': ''}
        # End changes, comment "path" arbitrary added

        if isinstance(custom_query, dict):
            # Update the parsed query with extra query dictionary. This may
            # override parsed query options.
            parsedquery.update(custom_query)
        results = catalog(**parsedquery)
        if getattr(results, 'actual_result_count', False) and limit\
                and results.actual_result_count > limit:
            results.actual_result_count = limit

        if not brains:
            results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, start=b_start)
        return results
