Changelog
=========


1.0 (2018-06-20)
----------------

- Make widget compatible with `eea.facetednavigation >= 10.0`.
  This makes it no more compatible with older version.
  [gbastien]
- Make package installable on both Plone4 and Plone5.
  [gbastien]
- Rely on `plone.app.contenttypes` instead `plone.app.collection`.
  [gbastien]
- Do not break to display the facetednavigation_view if no collection widget
  defined, it is the case when just enabling the faceted navigation on a new
  folder.
  [gbastien]
- Added field `enabled` (default=True) on a DashboardCollection make it possible
  to disable it so it is no more displayed in the collection widget (portlet).
  We specifically do not use a workflow for DashboardCollection.
  [gbastien]

0.9 (2018-05-25)
----------------

- Moved here some methods from imio.dashboard:
  _get_criterion, getCollectionLinkCriterion, getCurrentCollection
  [sgeulette]
- facetednavigation_view override to manage default collection widget redirection
  [sgeulette]
- Added portal attribute on category view.
  [sgeulette]

0.8 (2018-05-03)
----------------

- Fix wrong release version 0.7.
  [gbastien]

0.7 (2018-05-03)
----------------

- Removed useless parameter `query` from `CollectionVocabulary.__call__`.
  [gbastien]
- Use `zope.globalrequest.getRequest` and not `context.REQUEST`
  to get the REQUEST.
  [gbastien]

0.6 (2016-12-07)
----------------

- Add an option force_redirect_to in CollectionVocabulary to force generating
  no_redirect=1 urls for all collections.
  [vincentfretin]

- Don't modify the title of the page if the h1 has class dontupdate.
  [vincentfretin]

- Fix bug with DateTime in kept_criteria_as_json.
  [cedricmessiant]


0.5 (2016-05-13)
----------------

- Added plone.app.collection as a real dependency, this way it is present
  and we make sure that the profile is installed.
  [gbastien]


0.4 (2016-03-29)
----------------

- Adapted tests for eea.facetednavigation 8.8, moved to the collective,
  prepare for release on pypi.python.org.
  [gbastien]


0.3 (2016-03-03)
----------------

- Display number of collection items in the term view. Override
  display_number_of_items method if you want to alter this behaviour.
  [cedricmessiant]


0.2 (2015-09-03)
----------------

- The context for @@render_collection_widget_category is now the category
  (folder) and the context for @@render_collection_widget_term is the
  collection. (closes #11677)
  [vincentfretin]

- When generating link to sub faceted, make sure every default values are
  correctly initialized, especially value of the Collection widget for which
  the id could be different than current faceted Collection widget id
  [gbastien]

- If we use functionnality of sub folders where faceted navigation is enabled,
  and the default collection is on one of these subfolders, do not redirect to
  this default collection if we use the 'folder_contents' of the root folder or
  user is systematically redirected to the subfolder and it is not possible
  anymore to access on the root folder
  [gbastien]

- Added portal_url attribute in RenderCategoryView
  [sgeulette]

0.1 (2015-07-14)
----------------

- Initial release.
  [IMIO]
