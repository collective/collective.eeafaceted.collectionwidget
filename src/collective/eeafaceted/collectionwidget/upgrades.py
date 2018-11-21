# -*- coding: utf-8 -*-

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api

import logging
logger = logging.getLogger('collective.eeafaceted.collectionwidget')


def upgrade_to_3(context):
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(object_provides=IFacetedNavigable.__identifier__)
    for brain in brains:
        obj = brain.getObject()
        criterias = ICriteria(obj)
        changes = False
        for cid, crit in criterias.items():
            if crit.get('vocabulary', u'') in (u'imio.dashboard.conditionawarecollectionvocabulary',
                                               u'imio.dashboard.cachedcollectionvocabulary'):
                crit.vocabulary = u'collective.eeafaceted.collectionwidget.cachedcollectionvocabulary'
                changes = True
                logger.info('Criterion {} updated on object {}'.format(cid, brain.getPath()))
        if changes:
            criterias.criteria._p_changed = 1
