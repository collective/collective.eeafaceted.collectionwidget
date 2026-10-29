*** Settings ***
Documentation  The DashboardCollection content type, added through the Plone UI.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  collectionwidget.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
Add a DashboardCollection to a faceted folder
    Create a faceted folder
    Create a page  faceted  Alpha page
    Add a collection of the pages  faceted  Pages
    The status message contains  Item created
    The page title is  Pages
    The page lists  Alpha page
    Open the faceted folder  faceted
    The widget lists the collection  Pages

A DashboardCollection added without sort order lists its results in the widget
    [Documentation]  Known issue on Plone 4 (MIGRATION.md): the collection has no sort_on attribute,
    ...              the faceted query fails (AttributeError) and the results stay locked.
    [Tags]  plone4-bug
    Create a faceted folder
    Create a page  faceted  Alpha page
    Add a collection of the pages  faceted  Pages
    Open the faceted folder  faceted
    Select the collection  Pages
    The collection is selected  Pages
    The results list  Alpha page
