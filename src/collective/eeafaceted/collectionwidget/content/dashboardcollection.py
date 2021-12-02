# -*- coding: utf-8 -*-


from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from plone.app.contenttypes.content import Collection
from plone.app.querystring.queryparser import parseFormquery
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IDashboardCollection)
class DashboardCollection(Collection):
    """ """

    def displayCatalogQuery(self):
        """
          Return the stored query as a readable catalog query."""
        return parseFormquery(self, self.query)

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False,
                custom_query=None):
        """Overrided to not add the "path" in the qurey arbitrary,
           we do not need it and this index is very slow."""
        if custom_query is None:
            custom_query = {}
        querybuilder = getMultiAdapter((self, self.REQUEST),
                                       name='querybuilderresults')
        sort_order = 'reverse' if self.sort_reversed else 'ascending'
        if not b_size:
            b_size = getattr(self, 'item_count', 30)
        if not sort_on:
            sort_on = getattr(self, 'sort_on', None)
        if not limit:
            limit = getattr(self, 'limit', 1000)

        query = self.query

        # Handle INavigationRoot awareness as follows:
        # - If query is None or empty then do nothing.
        # - If query already contains a criteria for the index "path", then do
        #   nothing, since plone.app.querybuilder takes care of this
        #   already. (See the code of _path and _relativePath inside
        #   p.a.querystring.queryparser to understand).
        # - If query does not contain any criteria using the index "path", then
        #   add a criteria to match everything under the path "/" (which will
        #   be converted to the actual navigation root path by
        #   p.a.querystring).

        # collective.eeafaceted.collectionwidget
        # Begin changes: comment this part adding the path
        # if query:
        #     has_path_criteria = any(
        #         (criteria['i'] == 'path')
        #         for criteria in query
        #     )
        #     if not has_path_criteria:
        #         # Make a copy of the query to avoid modifying it
        #         query = list(self.query)
        #         query.append({
        #             'i': 'path',
        #             'o': 'plone.app.querystring.operation.string.path',
        #             'v': '/',
        #         })
        # collective.eeafaceted.collectionwidget
        # End changes: comment this part adding the path

        return querybuilder(
            query=query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=brains, custom_query=custom_query
        )
