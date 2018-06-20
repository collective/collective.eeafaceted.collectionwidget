# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.eeafaceted.collectionwidget import FacetedCollectionMessageFactory as _
from plone.app.contenttypes.interfaces import ICollection
from plone.autoform import directives as form
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveEeafacetedCollectionwidgetLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IWidgetDefaultValue(Interface):
    pass


class ICollectionCategories(Interface):
    pass


class IKeptCriteria(Interface):
    pass


class NotDashboardContextException(Exception):
    """ To be raised when a context has no faceted view defined on it. """


class NoFacetedViewDefinedException(NotDashboardContextException):
    """ To be raised when a context has no faceted view defined on it. """


class NoCollectionWidgetDefinedException(NotDashboardContextException):
    """ To be raised when a context has no collection widget defined on it. """


class IDashboardCollection(ICollection):
    """ """

    form.widget('showNumberOfItems', RadioFieldWidget)
    showNumberOfItems = schema.Bool(
        title=_(u'Show number of items in filter'),
        description=_(u'This will display the number of elements this search '
                      u'return in the widget (or portlet) collection. Take '
                      u'care that this is doing the search to display the result '
                      u'so enable it only if necessary.'),
        default=False,
        required=False,)

    form.widget('enabled', RadioFieldWidget)
    enabled = schema.Bool(
        title=_(u'Enabled?'),
        default=True,
        required=False,)
