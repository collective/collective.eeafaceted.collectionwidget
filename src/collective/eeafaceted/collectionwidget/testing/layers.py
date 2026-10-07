# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from eea.facetednavigation.interfaces import ICriteria
from plone.app.robotframework.content import Content
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.utils import disableCSRFProtection
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import zope
from zope.component import queryAdapter

import collective.eeafaceted.collectionwidget


class CollectiveEeafacetedCollectionwidgetLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ("collective.eeafaceted.collectionwidget", "Products.DateRecurringIndex")

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(
            package=collective.eeafaceted.collectionwidget, name="testing.zcml"
        )
        for p in self.products:
            zope.installProduct(app, p)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, "collective.eeafaceted.collectionwidget:testing")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory("Folder", "folder")
        folder = portal[folder_id]
        folder.reindexObject()

        # titled: Plone 6.2 renders no page heading for an empty title
        folder2_id = portal.invokeFactory("Folder", "folder2", title="Folder 2")
        folder2 = portal[folder2_id]
        folder2.reindexObject()
        folder2.unrestrictedTraverse("@@faceted_subtyper").enable()
        collection = portal.portal_types.DashboardCollection._constructInstance(
            folder2,
            id="collection_review_state",
            title="Review state",
            query=[
                {
                    "i": "review_state",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": ["published"],
                }
            ],
            showNumberOfItems=True,
            sort_on="",
            sort_reversed=False,
            tal_condition="",
            roles_bypassing_talcondition=[],
        )
        collection_uid = collection.UID()
        criteria = queryAdapter(folder2, ICriteria)
        # edit collection-link criteria
        criteria.edit("c1", default=collection_uid)
        # create a second collection without review_state criterion
        portal.portal_types.DashboardCollection._constructInstance(
            folder2,
            id="collection_wo_review_state",
            title="Creator",
            query=[
                {
                    "i": "Creator",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": ["_test_user_1"],
                }
            ],
            showNumberOfItems=True,
            sort_on="",
            sort_reversed=False,
            tal_condition="",
            roles_bypassing_talcondition=[],
        )

        # Commit so that the test browser sees these objects
        import transaction

        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        for p in reversed(self.products):
            zope.uninstallProduct(app, p)


FIXTURE = CollectiveEeafacetedCollectionwidgetLayer(name="FIXTURE")


INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


class SetFieldValue(Content):
    def set_field_value(self, uid, field, value, field_type):
        """plone.app.robotframework 3.0.0 doesn't disable the CSRF protection here (as
        create_content does): plone.protect silently aborts the change (MIGRATION.md).
        """
        disableCSRFProtection()
        return super().set_field_value(uid, field, value, field_type)


# REMOTE_LIBRARY_BUNDLE_FIXTURE with the fixed "Set field value" keyword
REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(SetFieldValue,) + REMOTE_LIBRARY_BUNDLE_FIXTURE.libraryBases[1:],
    name="CollectionwidgetRemoteLibrary:RobotRemote",
)


ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="ACCEPTANCE",
)
