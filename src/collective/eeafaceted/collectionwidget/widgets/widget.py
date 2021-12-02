# encoding: utf-8

from Acquisition import aq_parent
from collections import OrderedDict
from collective.eeafaceted.collectionwidget.interfaces import IKeptCriteria
from collective.eeafaceted.collectionwidget.interfaces import IWidgetDefaultValue
from DateTime import DateTime
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.radio.interfaces import IRadioSchema
from eea.facetednavigation.widgets.radio.widget import Widget as RadioWidget
from eea.facetednavigation.widgets.sorting.widget import Widget as SortingWidget
from plone import api
from plone.app.querystring import queryparser
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

import json


class ICollectionSchema(IRadioSchema):
    """ """


class CollectionWidget(RadioWidget):
    """A widget listing collections used as base query."""

    widget_type = 'collection-link'
    widget_label = 'Collection Link'
    faceted_field = False

    index = ViewPageTemplateFile('widget.pt')

    css_class = 'faceted-tagscloud-collection-widget'

    category_vocabulary = (
        'collective.eeafaceted.collectionwidget.collectioncategoryvocabulary'
    )

    def __init__(self, context, request, data=None):
        super(CollectionWidget, self).__init__(context, request, data)
        # widget context could not be current context but some distant context
        # look in eea.facetednavigation.criteria.handler.Criteria
        self.criteria = ICriteria(self.context)
        self.context = self.criteria.context
        if 'PUBLISHED' in request and hasattr(request['PUBLISHED'], 'context'):
            self.real_context = request['PUBLISHED'].context
        else:
            self.real_context = request['PARENTS'][0]
        # display the fieldset around the widget when rendered?
        self.display_fieldset = True
        self.portal = api.portal.get()

    def update(self):
        """Remove fields 'index' and 'catalog', unused."""
        super(CollectionWidget, self).update()
        default_group = self.groups[0]
        if 'index' in default_group.fields:
            del default_group.fields['index']
        if 'catalog' in default_group.widgets:
            del default_group.fields['catalog']
        if 'index' in default_group.widgets:
            del default_group.widgets['index']
        if 'catalog' in default_group.widgets:
            del default_group.widgets['catalog']

    def _initialize_widget(self):
        """ """
        self.grouped_vocabulary = self._generate_vocabulary()

    def __call__(self, **kwargs):
        # compute the vocabulary used in the widget
        self._initialize_widget()
        return super(CollectionWidget, self).__call__(**kwargs)

    def query(self, form):
        """ Get value from form and return a catalog dict query """
        # we receive the UID of the selected Collection
        # get the collection, compute the query and return it
        collection_uid = form.get(self.data.__name__, '')
        if collection_uid and not collection_uid == 'all':
            # get the collection and compute the query
            from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
            collection = getCurrentCollection(self.context)
            query = queryparser.parseFormquery(collection, collection.query)
            # use sort_on defined on the collection if it is
            # not already in the request.form
            # get the sort_on criterion and look in the request.form if it is used
            sort_on_is_used = False
            for criterion_id, criterion in self.criteria.items():
                if criterion.widget == SortingWidget.widget_type:
                    # criterion id in the request.form is like c0[]
                    if "{0}[]".format(criterion_id) in self.request.form:
                        sort_on_is_used = True
                    break
            if not sort_on_is_used:
                if collection.sort_on:
                    query['sort_on'] = collection.sort_on
                if collection.sort_reversed:
                    query['sort_order'] = collection.sort_reversed and 'descending' or ''
            return query
        return {}

    def count(self, brains, sequence=None):
        """
        """
        res = {}
        if not sequence:
            sequence = [term.token for term in self.vocabulary()]

        catalog = getToolByName(self.context, 'portal_catalog')
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue
            res[value] = len(
                catalog(self.query(form={self.data.__name__: value})))
        return res

    @property
    @memoize
    def default(self):
        """Return the default value"""
        default = super(CollectionWidget, self).default
        if not default:
            # it is possible to not select a default, it will have
            # same behaviour as selecting option "All"
            return default
        # call an adapter to get the correct value
        return self.adapter_default_value

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
        '''Given a p_collectionUID, get indexes managed by the collection.'''
        adapter = queryMultiAdapter((self.context, self),
                                    IKeptCriteria)
        res = adapter.compute(collection_uid)
        # DateTime are not json serializable, we convert them before
        for k, v in res.iteritems():
            if isinstance(v, DateTime):
                res[k] = v.ISO()

        return json.dumps(res)

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
    @memoize
    def categories(self):
        factory = getUtility(IVocabularyFactory, self.category_vocabulary)
        voc = factory(self.context)
        return voc

    def vocabulary(self):
        voc_id = self.data.get('vocabulary', None)
        voc = queryUtility(IVocabularyFactory, voc_id, None)
        if voc is None:
            return []

        return list(voc(self.context, self.real_context))

    def portal_vocabulary(self):
        values = []
        for term in self.vocabulary():
            values.append((term.value, term.title[0]))
        return values

    def _generate_vocabulary(self):
        voc = OrderedDict()
        # empty category
        voc[''] = {'collections': []}
        for term in self.categories:
            voc[term.token] = {'term': term, 'collections': []}

        categories_token = [term.token for term in self.categories]
        for term in self.vocabulary():
            collection = self.portal.unrestrictedTraverse(term.value)
            parent = aq_parent(collection)
            # collections directly added to context, no intermediate category
            if parent == self.context and parent.UID() not in categories_token:
                category = ''
            elif parent.UID() in categories_token:
                category = parent.UID()
            else:
                # parent is not visible, a subfolder private for current user
                continue

            voc[category]['collections'].append(term)

        # remove empty categories
        res = OrderedDict()
        for k, v in voc.items():
            if v['collections']:
                res[k] = v

        return res

    def render_category(self, term, view_name='@@render_collection_widget_category'):
        """ """
        collection = self.portal.unrestrictedTraverse(term.value)
        rendered_term = collection.unrestrictedTraverse(view_name)(widget=self)
        return rendered_term

    def render_term(self, term, category, view_name='@@render_collection_widget_term'):
        """ """
        collection = self.portal.unrestrictedTraverse(term.value)
        rendered_term = collection.unrestrictedTraverse(view_name)(term, category, widget=self)
        return rendered_term
