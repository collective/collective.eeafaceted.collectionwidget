Changelog
=========


0.2 (unreleased)
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
