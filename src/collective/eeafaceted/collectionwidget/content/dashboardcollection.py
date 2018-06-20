# -*- coding: utf-8 -*-


from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from plone.app.contenttypes.content import Collection
from plone.app.querystring.queryparser import parseFormquery
from zope.interface import implementer


@implementer(IDashboardCollection)
class DashboardCollection(Collection):
    """ """

    def displayCatalogQuery(self):
        """
          Return the stored query as a readable catalog query."""
        return parseFormquery(self, self.query)
