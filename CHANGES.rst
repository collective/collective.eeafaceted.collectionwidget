Changelog
=========


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
