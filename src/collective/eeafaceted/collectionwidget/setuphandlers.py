from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide the uninstall profile from the site creation and add-ons screens."""
        return ["collective.eeafaceted.collectionwidget:uninstall"]


def isNotCurrentProfile(context):
    return (
        context.readDataFile("collectiveeeafacetedcollectionwidget_marker.txt") is None
    )


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

    # if plone.app.contenttypes is not installed, we need the BrowserLayer so various
    # views like listing_view are available on DashboardCollection
    context._tool.runImportStepFromProfile(
        "profile-plone.app.contenttypes:default", "browserlayer"
    )
