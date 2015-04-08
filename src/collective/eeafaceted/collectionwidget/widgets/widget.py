# encoding: utf-8

import json
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

from eea.facetednavigation.widgets.radio.widget import Widget as RadioWidget

collection_edit_schema = RadioWidget.edit_schema.copy()
del collection_edit_schema["index"]
del collection_edit_schema["catalog"]


class CollectionBaseWidget(RadioWidget):
    edit_schema = collection_edit_schema
    category_vocabulary = (
        'collective.eeafaceted.collectionwidget.collectioncategoryvocabulary'
    )

    def __call__(self, **kwargs):
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

        catalog = getToolByName(self.context, 'portal_catalog')
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue
            res[value] = len(
                catalog(self.query(form={self.data.__name__: value})))
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

    def kept_criteria_as_json(self, collection_uid):
        '''Given a p_collectionUID, get indexes managed by the collection,
           and if it is also in advanced criteria, hide it.'''
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=collection_uid)
        res = []
        if brains:
            collection = brains[0].getObject()
            collection_criteria = queryparser.parseFormquery(collection, collection.query)
            advanced_criteria = self.advanced_criteria
            for k, v in advanced_criteria.items():
                if not v in collection_criteria:
                    res.append(k)
        return json.dumps(list(res))

    @property
    def advanced_criteria(self):
        '''Returns a dict containing advanced criteria, the key is the
           criterion id and the value is the managed index.'''
        faceted_config = queryMultiAdapter((self.context, self.request),
                                           name='configure_faceted.html')
        advanced_criteria = {}
        for criterion in faceted_config.get_criteria():
            if criterion.section == u'advanced':
                advanced_criteria[criterion.getId()] = criterion.index
        return advanced_criteria

    @property
    def advanced_criteria_as_json(self):
        return json.dumps(self.advanced_criteria.keys())

    @property
    def sortreversed(self):
        return bool(int(getattr(self.data, 'sortreversed', u'0') or u'0'))

    @property
    def hidealloption(self):
        return bool(int(getattr(self.data, 'hidealloption', u'0') or u'0'))

    @property
    def categories(self):
        factory = getUtility(IVocabularyFactory, self.category_vocabulary)
        voc = factory(self.context)
        return [(t.value, t.title) for t in voc]

    def _get_category_keys(self):
        return [id for (id, title) in self.categories]

    def _generate_vocabulary(self):
        voc = OrderedDict()
        for key, value in self.categories:
            voc[key] = []
        for key, value in self.vocabulary():
            voc[self._get_category(key)].append((key, value))
        return voc

    def _get_category(self, uid):
        """Return the category for a given uid"""
        collection = api.content.get(UID=uid)
        if collection is None:
            return u''
        else:
            parent_id = aq_parent(collection).getId()
            if parent_id in self._get_category_keys():
                return parent_id
            else:
                return u''
