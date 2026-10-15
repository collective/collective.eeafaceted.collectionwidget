*** Settings ***
Documentation  A faceted folder with a faceted sub-folder: the widget of the parent lists the collections of
...            the sub-folder, they open the sub-folder (FacetedDashboardView and the vocabulary redirect_to).
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  collectionwidget.robot
Test Setup  Open a manager browser with a faceted sub-folder
Test Teardown  Close all browsers


*** Test Cases ***
A collection of a faceted sub-folder opens that folder
    Open the faceted folder  faceted
    The category lists the collection  Sub folder  Sub collection
    Select the collection  Sub collection
    The location is  ${PLONE_URL}/faceted/sub-folder?no_redirect=1#c1=${SUB_COLLECTION_UID}
    The collection is selected  Sub collection
    The page title is  Sub collection
    The results list  Sub page

The parent faceted folder redirects to the sub-folder of its default collection
    Set the default collection  faceted  Sub collection
    Open the faceted folder  faceted
    The page URL is  ${PLONE_URL}/faceted/sub-folder
    The page title is  Sub folder


*** Keywords ***
Open a manager browser with a faceted sub-folder
    Open a manager browser
    Create a faceted folder  Sub folder
    Create a collection  faceted/sub-folder  Sub collection
    Create a page  faceted/sub-folder  Sub page
    Enable the faceted navigation  faceted/sub-folder
    ${uid}=  Path to uid  /${PLONE_SITE_ID}/faceted/sub-folder/sub-collection
    Set test variable  ${SUB_COLLECTION_UID}  ${uid}
