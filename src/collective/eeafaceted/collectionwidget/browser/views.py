# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion


class RenderCategoryView(BrowserView):

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

    def __call__(self, widget):
        self.widget = widget
        return self.index()


class RenderTermView(BrowserView):

    def display_number_of_items(self):
        """If true, display the number of items in the collection."""
        return True

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

    def __call__(self):
        criterion = getCollectionLinkCriterion(self.context)
        collectionUID = self.context.REQUEST.form.get('{0}[]'.format(criterion.__name__))
        if collectionUID or self.context.REQUEST.form.get('facetedQuery', '') or not criterion.default:
            return self.index()
        if not self.request['HTTP_REFERER'].endswith('configure_faceted.html') and \
           not self.request['URL'].endswith('folder_contents') and \
           not self.request.get('no_redirect', '0') == '1':
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(UID=criterion.default)
            if brains:
                collection = brains[0].getObject()
                container = collection.aq_inner.aq_parent
                if not container == self.context and \
                   IFacetedNavigable.providedBy(container):
                    self.request.RESPONSE.redirect(container.absolute_url())
                    return ''
        return self.index()
