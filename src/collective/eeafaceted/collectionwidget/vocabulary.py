# encoding: utf-8

from collective.behavior.talcondition.behavior import ITALCondition
from collective.behavior.talcondition.interfaces import ITALConditionable
from collective.eeafaceted.collectionwidget.interfaces import ICollectionCategories
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.interfaces import IFacetedNavigable
from imio.helpers.cache import get_cachekey_volatile
from plone import api
from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode
from zope.component import getAdapter
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class CollectionVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, real_context):
        self.context = context
        items = []
        current_url = context.absolute_url()
        for brain in self._brains(context):
            collection = brain.getObject()
            # if collection is ITALConditionable, evaluate the TAL condition
            # will not be evaluated if current user is Manager
            if ITALConditionable.providedBy(collection) and \
               not ITALCondition(collection).evaluate(extra_expr_ctx=self._extra_expr_ctx()):
                continue

            redirect_to = ''
            brain_folder_url = '/'.join(brain.getURL().split('/')[:-1])
            # if not in same folder and collection container is a faceted
            # we will redirect to this faceted to use criteria defined there
            if brain_folder_url != current_url or getRequest().get('force_redirect_to', False):
                collection_container = collection.aq_inner.aq_parent
                if IFacetedNavigable.providedBy(collection_container):
                    # find the collection-link widget
                    criteria = ICriteria(collection_container).criteria
                    for criterion in criteria:
                        if criterion.widget == CollectionWidget.widget_type:
                            redirect_to = self._compute_redirect_to(collection, criterion)
                            break

            items.append(SimpleTerm(brain.getPath(),
                                    brain.UID,
                                    (safe_unicode(brain.Title),
                                     redirect_to)))
        return SimpleVocabulary(items)

    def _brains(self, context):
        """ """
        root = context
        while IFacetedNavigable.providedBy(root.aq_inner.aq_parent):
            root = root.aq_inner.aq_parent
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(root.getPhysicalPath())),
            object_provides='plone.app.contenttypes.interfaces.ICollection',
            enabled=True,
            sort_on='getObjPositionInParent',
        )
        return brains

    def _compute_redirect_to(self, collection, criterion):
        """ """
        redirect_to = "{0}?no_redirect=1#{1}"
        # add a 'no_redirect=1' for links to collections
        collection_container = collection.aq_inner.aq_parent
        # build a base_query_url representing default parameters values
        criteria = ICriteria(collection_container).criteria
        default_criteria = []
        for criterion in criteria:
            # keep default of criteria in the "default"
            # section omitting the collection widget
            if criterion.section == u'default':
                if criterion.widget == CollectionWidget.widget_type:
                    default_criteria.append('{0}={1}'.format(criterion.__name__,
                                                             collection.UID()))
                elif criterion.default:
                    if criterion.widget == u'sorting':
                        # manage sort order criterion, received as c0=effective(reverse),
                        # changed for c0=effective&reversed=on
                        if criterion.default.endswith('(reverse)'):
                            default_criteria.append('{0}={1}&reversed=on'.format(
                                criterion.__name__,
                                criterion.default.replace('(reverse)', '')))
                        else:
                            default_criteria.append('{0}={1}'.format(criterion.__name__,
                                                                     criterion.default))
                    else:
                        default_criteria.append('{0}={1}'.format(criterion.__name__,
                                                                 criterion.default))
        query_url = '&'.join(default_criteria)
        return redirect_to.format(collection_container.absolute_url(),
                                  query_url)

    def _extra_expr_ctx(self):
        """To be overrided, this way, extra_expr_ctx is given to the
           expression evaluated on the DashboardCollection."""
        return {}


CollectionVocabularyFactory = CollectionVocabulary()


class CollectionCategoryVocabulary(object):
    implements(IVocabularyFactory)

    def __call___cachekey(method, self, context):
        '''cachekey method for self.__call__.'''
        root = context
        while IFacetedNavigable.providedBy(root.aq_inner.aq_parent):
            root = root.aq_inner.aq_parent
        return repr(root)

    @ram.cache(__call___cachekey)
    def CollectionCategoryVocabulary__call__(self, context):
        # find root
        root = context
        while IFacetedNavigable.providedBy(root.aq_inner.aq_parent):
            root = root.aq_inner.aq_parent
        adapter = getAdapter(root, ICollectionCategories)
        items = [SimpleTerm(value.getPath(), token, safe_unicode(value.Title))
                 for token, value in adapter.values]
        return SimpleVocabulary(items)

    # do ram.cache have a different key name
    __call__ = CollectionCategoryVocabulary__call__


CollectionCategoryVocabularyFactory = CollectionCategoryVocabulary()


class CachedCollectionVocabulary(CollectionVocabulary):

    def __call___cachekey(method, self, context, real_context):
        '''cachekey method for self.__call__.'''
        return self._cache_invalidation_key(context, real_context)

    def _cache_invalidation_key(self, context, real_context):
        '''The key will rely on :
           - current user as list of collections may vary depending on tal_condition per user;
           - a stored cache volatile that is destroyed if a DashboardCollection is modified somewhere;
           - the first facetednavigable context encountered when ascending context parents
             (useful when collections are defined in a single folder but displayed on various faceted container);
           - the application is accessed thru different portal_url.'''
        user = api.user.get_current().getId()
        date = get_cachekey_volatile('collective.eeafaceted.collectionwidget.cachedcollectionvocabulary')
        parent = context
        while not IFacetedNavigable.providedBy(parent) and parent.meta_type != 'Plone Site':
            parent = parent.aq_parent
        portal_url = api.portal.get().absolute_url()
        if getRequest().get('force_redirect_to', False):
            return user, date, repr(parent), portal_url, real_context.portal_type
        else:
            return user, date, repr(parent), portal_url

    @ram.cache(__call___cachekey)
    def CachedCollectionVocabulary__call__(self, context, real_context):
        """Same behaviour as the original CollectionVocabulary, just cached."""
        terms = super(CachedCollectionVocabulary, self).__call__(context, real_context)
        return terms

    # do ram.cache have a different key name
    __call__ = CachedCollectionVocabulary__call__


CachedCollectionVocabularyFactory = CachedCollectionVocabulary()
