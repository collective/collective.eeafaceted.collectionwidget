# -*- coding: utf-8 -*-

from plone.indexer import indexer
from plone.app.contenttypes.interfaces import ICollection


@indexer(ICollection)
def enabled(obj):
    """
    Indexes the 'enabled' attribute.
    """
    return getattr(obj, 'enabled', True)
