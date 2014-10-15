# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveEeafacetedCollectionwidgetLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IWidgetDefaultValue(Interface):
    pass


class ICollectionAdvancedFilter(Interface):
    pass


class ICollectionCategories(Interface):
    pass
