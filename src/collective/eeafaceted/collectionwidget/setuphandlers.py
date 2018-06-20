# -*- coding: utf-8 -*-


def isNotCurrentProfile(context):
    return context.readDataFile("collectiveeeafacetedcollectionwidget_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

    # if plone.app.contenttypes is not installed, we need the BrowserLayer so various
    # views like listing_view are available on DashboardCollection
    context._tool.runImportStepFromProfile('profile-plone.app.contenttypes:default', 'browserlayer')
