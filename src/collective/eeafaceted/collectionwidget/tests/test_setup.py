# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from ..testing.testcase import IntegrationTestCase
from collective.eeafaceted.collectionwidget import FacetedCollectionMessageFactory as _
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from Products.CMFPlone.utils import getFSVersionTuple
from zope.component import queryUtility
from zope.i18n import translate


def registered_resources(portal):
    """Ids of the CSS and JS resources registered in the site."""
    if getFSVersionTuple()[0] < 5:
        return (
            portal.portal_css.getResourceIds()
            + portal.portal_javascripts.getResourceIds()
        )
    raise NotImplementedError(
        "Plone 6: read the resource registry (MIGRATION.md phase 7)"
    )


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.collectionwidget into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.eeafaceted.collectionwidget is installed with portal_quickinstaller."""
        self.assertTrue(
            self.installer.isProductInstalled("collective.eeafaceted.collectionwidget")
        )

    def test_uninstall(self):
        """Test if collective.eeafaceted.collectionwidget is cleanly uninstalled."""
        self.installer.uninstallProducts(["collective.eeafaceted.collectionwidget"])
        self.assertFalse(
            self.installer.isProductInstalled("collective.eeafaceted.collectionwidget")
        )

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveEeafacetedCollectionwidgetLayer is registered as well as
        the plone.app.contenttypes BrowserLayer that is necessary for default listing_view."""
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
        self.assertTrue(fti.global_allow)
        self.assertEqual(
            tuple(fti.behaviors),
            (
                "plone.app.content.interfaces.INameFromTitle",
                "plone.app.contenttypes.behaviors.collection.ICollection",
                "collective.behavior.talcondition.behavior.ITALCondition",
                "plone.app.dexterity.behaviors.discussion.IAllowDiscussion",
                "plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation",
                "plone.app.dexterity.behaviors.metadata.IDublinCore",
                "plone.app.contenttypes.behaviors.richtext.IRichText",
                "plone.app.relationfield.behavior.IRelatedItems",
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

    # cssregistry.xml, jsregistry.xml
    def test_resources(self):
        resources = registered_resources(self.portal)
        for resource in (
            "++resource++collective.eeafaceted.collectionwidget.view.css",
            "++resource++collective.eeafaceted.collectionwidget.edit.css",
            "++resource++collective.eeafaceted.collectionwidget/collective.eeafaceted.collectionwidget.css",
            "++resource++collective.eeafaceted.collectionwidget.widgets.view.js",
            "++resource++collective.eeafaceted.collectionwidget.widgets.edit.js",
        ):
            self.assertIn(resource, resources)

    # locales
    def test_translations(self):
        self.assertEqual(
            translate(_("DashboardCollection"), target_language="fr"),
            "Collection pour tableau de bord",
        )
        self.assertEqual(
            translate(_("Hide category"), target_language="fr"), u"Cacher la catégorie"
        )
        self.assertEqual(
            translate(_("Show number of items in filter"), target_language="fr"),
            u"Afficher le nombre d'éléments",
        )
