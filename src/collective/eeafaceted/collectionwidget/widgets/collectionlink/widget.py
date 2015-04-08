# encoding: utf-8

from eea.facetednavigation.widgets import ViewPageTemplateFile
from collective.eeafaceted.collectionwidget.widgets.widget import (
    CollectionBaseWidget
)


class Widget(CollectionBaseWidget):

    widget_type = 'collection-link'
    widget_label = 'Collection Link'

    index = ViewPageTemplateFile('widget.pt')

    view_js = '++resource++collective.eeafaceted.collectionwidget.widgets.collectionlink.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.tagscloud.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.tagscloud.view.css'
    edit_css = '++resource++eea.facetednavigation.widgets.tagscloud.edit.css'
    css_class = 'faceted-tagscloud-widget'
