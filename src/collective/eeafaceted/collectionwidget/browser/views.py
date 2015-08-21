# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class RenderCategoryView(BrowserView):

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        self.portal_url = getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

    def __call__(self, category, widget):
        self.category = category
        self.widget = widget
        return self.index()


class RenderTermView(BrowserView):

    def __call__(self, term, category, widget):
        self.term = term
        self.category = category
        self.widget = widget
        return self.index()
