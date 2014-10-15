# encoding: utf-8

from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.radio.widget import Widget as RadioWidget
from collective.eeafaceted.collectionwidget.widgets.widget import (
    CollectionBaseWidget
)


class Widget(CollectionBaseWidget, RadioWidget):

    widget_type = 'collection-radio'
    widget_label = 'Collection Radio'
    category_vocabulary = (
        'collective.eeafaceted.collectionwidget.collectioncategoryvocabulary'
    )

    index = ViewPageTemplateFile('widget.pt')
