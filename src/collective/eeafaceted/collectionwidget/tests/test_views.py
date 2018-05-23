# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.tests.test_widget import BaseWidgetCase
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from zope.component import getMultiAdapter


class TestViews(BaseWidgetCase):
    """Test the views."""

    def test_FacetedDashboardView(self):
        subtyper = getMultiAdapter((self.category1, self.request),
                                   name=u'faceted_subtyper')
        subtyper.enable()
        # enabling a faceted will redirect to it, so, cancel this
        self.request.RESPONSE.status = 200

        # when default in self.folder, not redirected already at the right place
        view = getMultiAdapter((self.folder, self.request), name=u'facetednavigation_view')
        crit = getCollectionLinkCriterion(self.folder)
        crit.default = self.collection2.UID()
        ret = view()
        self.assertIn('Base collections', ret)
        self.assertEquals(self.request.RESPONSE.status, 200)

        # now set default on a collection of the subfolder
        crit.default = self.collection1.UID()

        # not redirected if we are on folder/folder_contents or folder/configure_faceted.html
        # or it is no more possible to access the folder actions, always redirected to subfolder...
        self.request['URL'] = self.folder.absolute_url() + '/folder_contents'
        ret = view()
        self.assertIn('Base collections', ret)
        self.assertEquals(self.request.RESPONSE.status, 200)
        folderURL = self.folder.absolute_url()
        self.request['URL'] = folderURL
        self.request['HTTP_REFERER'] = self.folder.absolute_url() + '/configure_faceted.html'
        ret = view()
        self.assertIn('Base collections', ret)
        self.assertEquals(self.request.RESPONSE.status, 200)

        # we are redirected to the subfolder if accessing directly folder
        self.request['URL'] = folderURL
        self.request['HTTP_REFERER'] = folderURL
        ret = view()
        self.assertFalse(ret)
        self.assertEquals(self.request.RESPONSE.status, 302)
        self.assertEquals(self.request.RESPONSE.getHeader('location'), self.category1.absolute_url())
