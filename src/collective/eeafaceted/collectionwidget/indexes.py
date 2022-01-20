# -*- coding: utf-8 -*-

from plone.app.contenttypes.interfaces import ICollection
from plone.indexer import indexer


@indexer(ICollection)
def enabled(obj):
    """
    Indexes the 'enabled' attribute.
    """
    return getattr(obj, 'enabled', True)
