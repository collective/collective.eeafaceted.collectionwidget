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


def safe_encode(term):
    if isinstance(term, unicode):
        # no need to use portal encoding for transitional encoding from
        # unicode to ascii. utf-8 should be fine.
        term = term.encode('utf-8')
    return term


class CollectionVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        self.context = context

        results = [(b.Title, b.UID) for b in self.brains]
        items = [
            SimpleTerm(uid, uid, safe_unicode(title))
            for title, uid in results
            if query is None or safe_encode(query) in safe_encode(title)
        ]
        sorted(items)

        return SimpleVocabulary(items)

    @property
    def brains(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog({'portal_type': 'Collection'})


CollectionVocabularyFactory = CollectionVocabulary()


class CollectionCategoryVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        adapter = getAdapter(context, ICollectionCategories)
        items = [SimpleTerm(key, key, value) for key, value in adapter.values]
        return SimpleVocabulary(items)


CollectionCategoryVocabularyFactory = CollectionCategoryVocabulary()
