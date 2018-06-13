# -*- coding: utf-8 -*-

import json
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api

from config import NO_COLLECTIONWIDGET_EXCEPTION_MSG, NO_FACETED_EXCEPTION_MSG
from interfaces import NoCollectionWidgetDefinedException, NoFacetedViewDefinedException
from widgets.widget import CollectionWidget


def _get_criterion(faceted_context, criterion_type):
    """Return the given criterion_type instance of a
       context with a faceted navigation/search view on it."""
    if not IFacetedNavigable.providedBy(faceted_context):
        raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)

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


def getCurrentCollection(faceted_context):
    """Return the Collection currently used by the faceted :
       - first get the collection criterion;
       - then look in the request the used UID and get the corresponding Collection."""
    criterion = getCollectionLinkCriterion(faceted_context)
    collectionUID = faceted_context.REQUEST.form.get('{0}[]'.format(criterion.__name__))
    # if not collectionUID, maybe we have a 'facetedQuery' in the REQUEST
    if not collectionUID and \
       ('facetedQuery' in faceted_context.REQUEST.form and faceted_context.REQUEST.form['facetedQuery']):
        query = json.loads(faceted_context.REQUEST.form['facetedQuery'])
        collectionUID = query.get(criterion.__name__)
    if collectionUID:
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(UID=collectionUID)[0].getObject()


def _updateDefaultCollectionFor(folderObj, default_uid):
    """Use p_default_uid as the default collection selected
       for the CollectionWidget used on p_folderObj."""
    # folder should be a facetednav
    if not IFacetedNavigable.providedBy(folderObj):
        raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)

    criterion = getCollectionLinkCriterion(folderObj)
    criterion.default = default_uid
    # make change persist!
    ICriteria(folderObj).criteria._p_changed = True
