# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from plone.app.contenttypes.content import Collection
from zope.interface import implementer


@implementer(IDashboardCollection)
class DashboardCollection(Collection):
    """ """