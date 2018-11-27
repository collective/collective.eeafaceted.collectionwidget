# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.content.dashboardcollection import IDashboardCollection
from collective.eeafaceted.collectionwidget.interfaces import NoCollectionWidgetDefinedException
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api
from Products.Five.browser import BrowserView


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

    def display_number_of_items(self):
        """Display number of items in the collection."""
        if not IDashboardCollection.providedBy(self.context):
            return True
        return self.context.showNumberOfItems

    def number_of_items(self):
        """Return the number of items in the collection."""
        return len(self.context.results())

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
                catalog = api.portal.get_tool('portal_catalog')
                brains = catalog(UID=criterion.default)
                if brains:
                    collection = brains[0].getObject()
                    container = collection.aq_inner.aq_parent
                    if not container == criteria_holder and \
                       IFacetedNavigable.providedBy(container):
                        self.request.RESPONSE.redirect(container.absolute_url())
                        return ''
        return self.index()
