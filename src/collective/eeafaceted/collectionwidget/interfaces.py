# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

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
