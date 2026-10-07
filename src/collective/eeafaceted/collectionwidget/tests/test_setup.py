# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from ..testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget import FacetedCollectionMessageFactory as _
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IBundleRegistry
from plone.base.utils import get_installer
from plone.behavior.interfaces import IBehavior
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate


def registered_bundles():
    """Resource registry bundles, by name."""
    return getUtility(IRegistry).collectionOfInterface(
        IBundleRegistry, prefix="plone.bundles", check=False
    )


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.collectionwidget into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.eeafaceted.collectionwidget is installed."""
        self.assertTrue(
            self.installer.is_product_installed(
                "collective.eeafaceted.collectionwidget"
            )
        )

    def test_uninstall(self):
        """Test if collective.eeafaceted.collectionwidget is cleanly uninstalled."""
        from collective.eeafaceted.collectionwidget.interfaces import (
            ICollectiveEeafacetedCollectionwidgetLayer,
        )
        from plone.browserlayer import utils

        self.installer.uninstall_product("collective.eeafaceted.collectionwidget")
        self.assertFalse(
            self.installer.is_product_installed(
                "collective.eeafaceted.collectionwidget"
            )
        )
        self.assertNotIn(
            ICollectiveEeafacetedCollectionwidgetLayer, utils.registered_layers()
        )
        self.assertFalse(
            [name for name in registered_bundles() if "collectionwidget" in name]
        )
        self.assertNotIn(
            "plone.icon.contenttype/dashboardcollection", getUtility(IRegistry)
        )

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveEeafacetedCollectionwidgetLayer is registered as well as
        the plone.app.contenttypes BrowserLayer that is necessary for default listing_view.
        """
        from collective.eeafaceted.collectionwidget.interfaces import (
            ICollectiveEeafacetedCollectionwidgetLayer,
        )
        from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
        from plone.browserlayer import utils

        self.assertIn(
            ICollectiveEeafacetedCollectionwidgetLayer, utils.registered_layers()
        )
        self.assertIn(IPloneAppContenttypesLayer, utils.registered_layers())

    # types.xml, types/DashboardCollection.xml
    def test_types(self):
        fti = self.portal.portal_types.DashboardCollection
        self.assertEqual(fti.meta_type, "Dexterity FTI")
        self.assertEqual(
            fti.klass,
            "collective.eeafaceted.collectionwidget.content.dashboardcollection.DashboardCollection",
        )
        self.assertEqual(
            fti.schema,
            "collective.eeafaceted.collectionwidget.interfaces.IDashboardCollection",
        )
        self.assertEqual(
            fti.add_permission,
            "collective.eeafaceted.collectionwidget.addDashboardCollection",
        )
        self.assertEqual(fti.default_view, "listing_view")
        # icon_expr: name of the icon, registered in registry.xml
        self.assertEqual(fti.icon_expr, "string:contenttype/dashboardcollection")
        self.assertEqual(
            self.portal.restrictedTraverse("@@iconresolver").url(
                "contenttype/dashboardcollection"
            ),
            "http://nohost/plone/++resource++collective.eeafaceted.collectionwidget/"
            "dashboardcollection.png",
        )
        self.assertTrue(fti.global_allow)
        self.assertEqual(
            tuple(fti.behaviors),
            (
                "plone.namefromtitle",
                "plone.collection",
                "collective.behavior.talcondition.behavior.ITALCondition",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.dublincore",
                "plone.richtext",
                "plone.relateditems",
            ),
        )
        # every behavior exists
        self.assertEqual(
            [b for b in fti.behaviors if queryUtility(IBehavior, name=b) is None], []
        )

    # catalog.xml
    def test_catalog(self):
        catalog = self.portal.portal_catalog
        self.assertIn("enabled", catalog.indexes())
        self.assertEqual(catalog.Indexes["enabled"].meta_type, "BooleanIndex")

    # rolemap.xml
    def test_rolemap(self):
        roles = [
            r["name"]
            for r in self.portal.rolesOfPermission(
                "collective.eeafaceted.collectionwidget: Add DashboardCollection"
            )
            if r["selected"]
        ]
        self.assertEqual(roles, ["Manager", "Site Administrator"])
        # the add permission drives the add menu
        folder = self.portal.folder
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        self.assertNotIn(
            "DashboardCollection", [t.getId() for t in folder.allowedContentTypes()]
        )
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        self.assertIn(
            "DashboardCollection", [t.getId() for t in folder.allowedContentTypes()]
        )

    # workflows.xml
    def test_workflows(self):
        self.assertEqual(
            self.portal.portal_workflow.getChainForPortalType("DashboardCollection"), ()
        )

    # registry.xml
    def test_resources(self):
        bundles = registered_bundles()
        # forms of the DashboardCollection
        self.assertEqual(
            bundles["collectionwidget"].csscompilation,
            "++resource++collective.eeafaceted.collectionwidget/"
            "collective.eeafaceted.collectionwidget.css",
        )
        # widget, loaded after the eea.facetednavigation bundle it extends, deferred as it is
        for name, js, css, depends in (
            (
                "faceted.collectionwidget.view",
                "++resource++collective.eeafaceted.collectionwidget.widgets.view.js",
                "++resource++collective.eeafaceted.collectionwidget.view.css",
                "faceted.view",
            ),
            (
                "faceted.collectionwidget.edit",
                "++resource++collective.eeafaceted.collectionwidget.widgets.edit.js",
                None,
                "faceted.edit",
            ),
        ):
            bundle = bundles[name]
            self.assertTrue(bundle.enabled)
            self.assertEqual(
                (bundle.jscompilation, bundle.csscompilation, bundle.depends),
                (js, css, depends),
            )
            self.assertIn(depends, bundles)
            self.assertTrue(bundle.load_defer)
            self.assertFalse(bundle.load_async)
        # every resource exists
        for bundle in ("collectionwidget", "faceted.collectionwidget.view"):
            self.portal.restrictedTraverse(bundles[bundle].csscompilation)
        for bundle in (
            "faceted.collectionwidget.view",
            "faceted.collectionwidget.edit",
        ):
            self.portal.restrictedTraverse(bundles[bundle].jscompilation)

    # locales
    def test_translations(self):
        self.assertEqual(
            translate(_("DashboardCollection"), target_language="fr"),
            "Collection pour tableau de bord",
        )
        self.assertEqual(
            translate(_("Hide category"), target_language="fr"), "Cacher la catégorie"
        )
        self.assertEqual(
            translate(_("Show number of items in filter"), target_language="fr"),
            "Afficher le nombre d'éléments",
        )
