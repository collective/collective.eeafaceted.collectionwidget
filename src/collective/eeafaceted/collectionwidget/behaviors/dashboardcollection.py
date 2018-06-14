# -*- coding: utf-8 -*-

from plone.app.contenttypes.behaviors.collection import Collection
from plone.app.contenttypes.behaviors.collection import ICollection as pac_ICollection
from plone.autoform import directives as form
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema

from Products.CMFPlone.interfaces.syndication import ISyndicatable

from plone.app.querystring.queryparser import parseFormquery
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from collective.eeafaceted.collectionwidget import FacetedCollectionMessageFactory as _


# !!! it is important that the interface of the behavior is named ICollection
# because some javascript looks for ICollection-sort_on/ICollection-sort_reversed
# fields and it only works when behavior interface has the correct name

@provider(IFormFieldProvider, ISyndicatable)
class ICollection(pac_ICollection):
    """ """

    form.widget('showNumberOfItems', RadioFieldWidget)
    showNumberOfItems = schema.Bool(
        title=_(u'Show number of items in filter'),
        default=False,
        required=False,)

    form.omitted('limit')
    form.omitted('item_count')


@implementer(ICollection)
@adapter(IDexterityContent)
class DashboardCollection(Collection):
    """A Collection used in our dashboards"""

    # Getters and setters for our fields.

    def _set_showNumberOfItems(self, value):
        self.context.showNumberOfItems = value

    def _get_showNumberOfItems(self):
        return getattr(self.context, 'showNumberOfItems', False)

    showNumberOfItems = property(_get_showNumberOfItems, _set_showNumberOfItems)

    def displayCatalogQuery(self):
        """
          Return the stored query as a readable catalog query."""
        return parseFormquery(self, self.query)
