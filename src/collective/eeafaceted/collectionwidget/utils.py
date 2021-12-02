# -*- coding: utf-8 -*-

from config import NO_COLLECTIONWIDGET_EXCEPTION_MSG
from config import NO_FACETED_EXCEPTION_MSG
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.events import FacetedGlobalSettingsChangedEvent
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from imio.helpers.content import uuidToObject
from interfaces import NoCollectionWidgetDefinedException
from interfaces import NoFacetedViewDefinedException
from widgets.widget import CollectionWidget
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.globalrequest import getRequest

import json


def _get_criterion(faceted_context, criterion_type, raise_on_error=True):
    """Return the given criterion_type instance of a
       context with a faceted navigation/search view on it."""
    if not IFacetedNavigable.providedBy(faceted_context):
        if raise_on_error:
            raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)
        else:
            return None

    criteria = ICriteria(faceted_context).criteria
    for criterion in criteria:
        if criterion.widget == criterion_type:
            return criterion


def getCollectionLinkCriterion(faceted_context):
    """Return the CollectionLink criterion used by faceted_context."""
    criterion = _get_criterion(faceted_context,
                               criterion_type=CollectionWidget.widget_type)
    if not criterion:
        raise NoCollectionWidgetDefinedException(NO_COLLECTIONWIDGET_EXCEPTION_MSG)

    return criterion


def getCurrentCollection(faceted_context, caching=True):
    """Return the Collection currently used by the faceted :
       - first get the collection criterion;
       - then look in the request the used UID and get the corresponding Collection.
       If p_caching is True, the collection is stored in request cache."""
    collection = None
    if caching:
        request = getRequest()
        if request:
            key = 'collectionwidget-utils-getCurrentCollection-{0}'.format(faceted_context.UID())
            cache = IAnnotations(request)
            collection = cache.get(key, None)
        else:
            caching = False

    if collection is None:
        criterion = getCollectionLinkCriterion(faceted_context)
        collectionUID = faceted_context.REQUEST.form.get('{0}[]'.format(criterion.__name__))
        # if not collectionUID, maybe we have a 'facetedQuery' in the REQUEST
        if not collectionUID and \
           ('facetedQuery' in faceted_context.REQUEST.form and
                faceted_context.REQUEST.form['facetedQuery']):
            query = json.loads(faceted_context.REQUEST.form['facetedQuery'])
            collectionUID = query.get(criterion.__name__)
        if collectionUID:
            collection = uuidToObject(collectionUID, unrestricted=True)
        if caching:
            cache[key] = collection

    return collection


def _updateDefaultCollectionFor(folderObj, default_uid):
    """Use p_default_uid as the default collection selected
       for the CollectionWidget used on p_folderObj."""
    # folder should be a facetednav
    if not IFacetedNavigable.providedBy(folderObj):
        raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)

    criterion = getCollectionLinkCriterion(folderObj)
    # use ICriteria.edit so change is persisted
    ICriteria(folderObj).edit(criterion.__name__, **{'default': default_uid})
    # notify that settings changed
    notify(FacetedGlobalSettingsChangedEvent(folderObj))
