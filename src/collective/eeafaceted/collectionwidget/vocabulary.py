# encoding: utf-8

from Products.CMFPlone.utils import safe_unicode
from collective.eeafaceted.collectionwidget.interfaces import (
    ICollectionCategories
)
from plone import api
from zope.component import getAdapter
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class CollectionVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        self.context = context

        results = [(b.Title, b.UID) for b in self.brains]
        items = [
            SimpleTerm(uid, uid, safe_unicode(title))
            for title, uid in results
        ]
        sorted(items)

        return SimpleVocabulary(items)

    @property
    def brains(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.context.getPhysicalPath())),
            object_provides='plone.app.collection.interfaces.ICollection',
            sort_on='getObjPositionInParent'
        )
        return brains


CollectionVocabularyFactory = CollectionVocabulary()


class CollectionCategoryVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        adapter = getAdapter(context, ICollectionCategories)
        items = [SimpleTerm(key, key, value) for key, value in adapter.values]
        return SimpleVocabulary(items)


CollectionCategoryVocabularyFactory = CollectionCategoryVocabulary()
