
.. image:: https://travis-ci.org/IMIO/collective.eeafaceted.collectionwidget.svg
  :target: https://travis-ci.org/IMIO/collective.eeafaceted.collectionwidget


.. image:: https://coveralls.io/repos/IMIO/collective.eeafaceted.collectionwidget/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/IMIO/collective.eeafaceted.collectionwidget?branch=master

.. image:: https://circleci.com/gh/IMIO/collective.eeafaceted.collectionwidget.svg?&style=shield
  :target: https://circleci.com/gh/IMIO/collective.eeafaceted.collectionwidget

==========================================================================
collective.eeafaceted.collectionwidget
==========================================================================

Package adding a widget for eea.facetednavigation that list collections as base searches

* `Source code @ GitHub <https://github.com/IMIO/collective.eeafaceted.collectionwidget>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/IMIO/collective.eeafaceted.collectionwidget>`_

How it works
============

Once installed, a new widget `Collection Link` is available while configuring the faceted navigation.  It will display a list of Collections (plone.app.collection) that will be used as base searches.

Installation
============

To install `collective.eeafaceted.collectionwidget` you simply add ``collective.eeafaceted.collectionwidget``
to the list of eggs in your buildout, use make run to launch buildout and start Plone.
Then, install `collective.eeafaceted.collectionwidget` using the Add-ons control panel.


Configuration
=============

All that is necessary when adding this kind of widget in a faceted navigation is to enter a name for the displayed widget and to select the vocabulary `collective.eeafaceted.collectionwidget.collectionvocabulary`.  It will automatically display the Collections contained in the folder the faceted navigation is configured on.  It is also possible to group Collections by category, to do so, instead of adding the Collections directly in the folder, you can create a subfolder that will contain the Collections.
