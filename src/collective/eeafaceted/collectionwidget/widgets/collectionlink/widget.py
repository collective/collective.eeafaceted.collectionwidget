# encoding: utf-8

from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.radio.widget import Widget as RadioWidget
from collective.eeafaceted.collectionwidget.widgets.widget import (
    CollectionBaseWidget
)


class Widget(CollectionBaseWidget, RadioWidget):

    widget_type = 'collection-link'
    widget_label = 'Collection Link'
    category_vocabulary = (
        'collective.eeafaceted.collectionwidget.collectioncategoryvocabulary'
    )

    index = ViewPageTemplateFile('widget.pt')

    view_js = '++resource++eea.facetednavigation.widgets.tagscloud.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.tagscloud.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.tagscloud.view.css'
    edit_css = '++resource++eea.facetednavigation.widgets.tagscloud.edit.css'
    css_class = 'faceted-tagscloud-widget'
