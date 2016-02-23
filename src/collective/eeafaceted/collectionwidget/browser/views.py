# -*- coding: utf-8 -*-
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class RenderCategoryView(BrowserView):

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        self.portal_url = getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

    def __call__(self, widget):
        self.widget = widget
        return self.index()


class RenderTermView(BrowserView):

    def display_number_of_items(self):
        """If true, display the number of items in the collection."""
        return True

    def number_of_items(self):
        """Return the number of items in the collection."""
        catalog = api.portal.get_tool('portal_catalog')
        return self.context.results().sequence_length

    def __call__(self, term, category, widget):
        self.term = term
        self.category = category
        self.widget = widget
        return self.index()
