# -*- coding: utf-8 -*-

from imio.helpers.content import uuidToObject
from plone.app.querystring import queryparser
from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from zope.globalrequest import getRequest


class DefaultValue(object):
    """If we  have a default value, check if it is still available
       it could have been deleted or used vocabulary could not contain it anymore.
       If it is the case, we fall back to first available collection."""
    def __init__(self, context, request, widget):
        self.value = widget.data.default
        existingCollectionUids = []
        for group in widget.grouped_vocabulary.values():
            for collection_term in group['collections']:
                existingCollectionUids.append(collection_term.token)
        if widget.data.default not in existingCollectionUids:
            self.value = existingCollectionUids and existingCollectionUids[0] or ''


class KeptCriteria(object):
    """This adapter makes it possible to override default implementation
       of which criteria are kept when changing from a collection to another.
       By default, this is done smartly by disabling criteria using indexes
       already managed by the selected collection."""

    def __init__(self, context, widget):
        self.context = context
        self.widget = widget
        self.request = getRequest()

    def compute(self, collection_uid):
        """ """
        res = {}
        # special case for the 'all' option where every criteria are kept
        if collection_uid == 'all':
            res = dict([(k, []) for k in self.widget.advanced_criteria])
        else:
            collection = uuidToObject(collection_uid, unrestricted=True)
            if collection:
                catalog = getToolByName(self.context, 'portal_catalog')
                collection_criteria = queryparser.parseFormquery(collection, collection.query)
                advanced_criteria = self.widget.advanced_criteria
                for wid, index in advanced_criteria.items():
                    if index not in collection_criteria:
                        res[wid] = []
                    else:
                        enabled_checkboxes = collection_criteria[index].get('query', [])
                        # special bypass for daterange, if we have a list of dates, we use []
                        if isinstance(catalog.Indexes.get(index), DateIndex) and \
                           isinstance(enabled_checkboxes, list):
                            enabled_checkboxes = []

                        if isinstance(enabled_checkboxes, basestring):
                            # the case {'Creator': {'query': 'test-user'}} go here
                            enabled_checkboxes = [enabled_checkboxes]

                        res[wid] = enabled_checkboxes
        return res
