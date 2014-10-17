# encoding: utf-8

from eea.facetednavigation.widgets import ViewPageTemplateFile
from collective.eeafaceted.collectionwidget.widgets.widget import (
    CollectionBaseWidget
)


class Widget(CollectionBaseWidget):

    widget_type = 'collection-radio'
    widget_label = 'Collection Radio'
    index = ViewPageTemplateFile('widget.pt')
