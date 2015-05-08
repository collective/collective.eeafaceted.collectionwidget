# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class RenderCategoryView(BrowserView):

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
