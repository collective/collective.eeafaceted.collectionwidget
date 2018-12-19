# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2018 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.helpers.cache import invalidate_cachekey_volatile_for
from plone import api


def onDashboardCollectionCreated(obj, event):
    '''Called whenever a DashboardCollection is created.'''
    invalidate_cachekey_volatile_for('collective.eeafaceted.collectionwidget.cachedcollectionvocabulary')


def onDashboardCollectionModified(obj, event):
    '''Called whenever a DashboardCollection is modified.'''
    invalidate_cachekey_volatile_for('collective.eeafaceted.collectionwidget.cachedcollectionvocabulary')


def onDashboardCollectionRemoved(obj, event):
    '''Called whenever a WF transition was triggered on a DashboardCollection.'''
    try:
        api.portal.get()
    except api.portal.CannotGetPortalError:
        return  # when deleting site
    invalidate_cachekey_volatile_for('collective.eeafaceted.collectionwidget.cachedcollectionvocabulary')
