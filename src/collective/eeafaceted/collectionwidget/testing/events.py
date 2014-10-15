# encoding: utf-8

from Products.GenericSetup.context import SnapshotImportContext
from Products.GenericSetup.interfaces import IBody
from eea.facetednavigation.interfaces import ICriteria
from zope.component import queryAdapter
from zope.component import queryMultiAdapter


def collection_faceted_enabled(context, event):
    # Add default widgets
    add_default_collection_widgets(context)

    # Reindex
    context.reindexObject(['object_provides', ])


def add_default_collection_widgets(context):
    criteria = queryAdapter(context, ICriteria)
    if not criteria:
        return

    # Configure widgets only for canonical (LinguaPlone only)
    getCanonical = getattr(context, 'getCanonical', None)
    if getCanonical:
        canonical = getCanonical()
        if context != canonical:
            return

    if criteria.keys():
        criteria.criteria = []

    widgets = context.unrestrictedTraverse('@@default_collection_widgets.xml')
    if not widgets:
        return

    xml = widgets()
    environ = SnapshotImportContext(context, 'utf-8')
    importer = queryMultiAdapter((context, environ), IBody)
    if not importer:
        return
    importer.body = xml
