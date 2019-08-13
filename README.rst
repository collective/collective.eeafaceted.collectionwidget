
.. image:: https://travis-ci.org/collective/collective.eeafaceted.collectionwidget.svg
  :target: https://travis-ci.org/collective/collective.eeafaceted.collectionwidget


.. image:: https://coveralls.io/repos/collective/collective.eeafaceted.collectionwidget/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/collective/collective.eeafaceted.collectionwidget?branch=master

==========================================================================
collective.eeafaceted.collectionwidget
==========================================================================

Package adding a widget for eea.facetednavigation that list collections as base searches

* `Source code @ GitHub <https://github.com/collective/collective.eeafaceted.collectionwidget>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/collective/collective.eeafaceted.collectionwidget>`_

How it works
============

Once installed, a new widget `Collection Link` is available while configuring the faceted navigation.
If you add Collections to a folder on which faceted navigation is enabled, the widget will display
the found Collections and use it as base searches.
A special content DashboardCollection is also provided, it is based on the Collection but use additional
behaviors :

- The 'DashboardCollection' behavior that provides an extra field showNumberOfItems, making it possible to display the counter on a per DashboardCollection basis;
- The 'TAL condition' behavior that adds a field into which defining a TAL expression that will make it possible to hide or show a Collection in the widget.

Installation
============

To install `collective.eeafaceted.collectionwidget` you simply add ``collective.eeafaceted.collectionwidget``
to the list of eggs in your buildout, use make run to launch buildout and start Plone.
Then, install `collective.eeafaceted.collectionwidget` using the Add-ons control panel.

Configuration
=============

All that is necessary when adding this kind of widget in a faceted navigation is to enter a name for the displayed widget and to select the vocabulary `collective.eeafaceted.collectionwidget.collectionvocabulary`.  It will automatically display the Collections contained in the folder the faceted navigation is configured on.  It is also possible to group Collections by category, to do so, instead of adding the Collections directly in the folder, you can create a subfolder that will contain the Collections.

eea.facetednavigation version
=============================

From version 1.0, the widget requires at least `eea.facetednavigation` 10.0 where widget is built using `z3c.form`.
If you are using `eea.facetednavigation` < 10.0, you need to use a version of `collective.eeafaceted.collectionwidget` < 1.0.

