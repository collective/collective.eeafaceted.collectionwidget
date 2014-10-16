# encoding: utf-8

from Products.CMFCore.utils import getToolByName
from collections import OrderedDict
from collective.eeafaceted.collectionwidget.interfaces import (
    IWidgetDefaultValue
)
from plone.app.querystring import queryparser
from plone import api
from Acquisition import aq_parent
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.schema.interfaces import IVocabularyFactory

from eea.facetednavigation.widgets.widget import Widget


class CollectionBaseWidget(Widget):

    def __call__(self, **kwargs):
        self.categories = self._get_categories()
        self.grouped_vocabulary = self._generate_vocabulary()
        return super(CollectionBaseWidget, self).__call__(**kwargs)

    def query(self, form):
        """ Get value from form and return a catalog dict query """
        # we receive the UID of the selected Collection
        # get the collection, compute the query and return it
        collection_uid = form.get(self.data.__name__, '')
        if collection_uid:
            # get the collection and compute the query
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(UID=collection_uid)
            collection = brains[0].getObject()
            return queryparser.parseFormquery(self.context, collection.query)
        return {}

    def count(self, brains, sequence=None):
        """
        """
        res = {}
        if not sequence:
            sequence = [key for key, value in self.vocabulary()]

        ctool = getToolByName(self.context, 'portal_catalog')
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue
            res[value] = len(
                ctool(self.query(form={self.data.__name__: value})))
        return res

    @property
    def default(self):
        """Return the default value"""
        default = super(CollectionBaseWidget, self).default
        if not default:
            default = self.adapter_default_value
        if not default and self.hidealloption is True:
            default = self.default_term_value
        return default

    @property
    def adapter_default_value(self):
        adapter = queryMultiAdapter((self.context, self.request, self),
                                    IWidgetDefaultValue)
        if adapter:
            return adapter.value

    @property
    def default_term_value(self):
        idx = self.sortreversed and -1 or 0
        terms = self.portal_vocabulary()
        if len(terms) > 0:
            return terms[idx][0]

    @property
    def sortreversed(self):
        return bool(int(getattr(self.data, 'sortreversed', u'0') or u'0'))

    @property
    def hidealloption(self):
        return bool(int(getattr(self.data, 'hidealloption', u'0') or u'0'))

    def _get_categories(self):
        factory = getUtility(IVocabularyFactory, self.category_vocabulary)
        voc = factory(self.context)
        return [(t.value, t.title) for t in voc]

    def _get_category_keys(self):
        return [id for (id, title) in self._get_categories()]

    def _generate_vocabulary(self):
        voc = OrderedDict()
        for key, value in self.categories:
            voc[key] = []
        for key, value in self.vocabulary():
            voc[self._get_category(key)].append((key, value))
        return voc

    def _get_category(self, uid):
        """Return the category for a given uid"""
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=uid)
        if brains:
            brain = brains[0]
            collection = brain.getObject()
        parent_id = aq_parent(collection).getId()
        if parent_id in self._get_category_keys():
            return parent_id
        else:
            return u''
