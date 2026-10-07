*** Settings ***
Documentation  The collection-link widget "Base collections" (c1) of a faceted folder.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  collectionwidget.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
Widget shows no collections or categories when folder is empty
    Create a faceted folder
    Open the faceted configuration  faceted
    The widget lists no collection

Widget does not show empty categories
    Create a faceted folder  News
    Open the faceted configuration  faceted
    The widget shows the category  News  ${False}
    Create a collection  faceted/news  Info
    Open the faceted configuration  faceted
    The widget shows the category  News
    The category lists the collection  News  Info

Widget shows collections in categories
    Create a faceted folder  News  Events
    Create a collection  faceted/news  Info
    Create a collection  faceted/events  Agenda
    Create a page  faceted  Info page
    Open the faceted folder  faceted
    The category lists the collection  News  Info
    The category lists the collection  Events  Agenda
    The collection shows its number of items  Info  1
    Select the collection  Info
    The collection is selected  Info
    The page title is  News: Info
    The results list  Info page

Faceted title matches selected collection
    Create a faceted folder
    Create a collection  faceted  Info
    Create a collection  faceted  Agenda
    Set the default collection  faceted  Info
    Open the faceted folder  faceted
    The collection is selected  Info
    The page title is  Info
    Select the collection  Agenda
    The collection is selected  Agenda
    The page title is  Agenda

Advanced criterion are disabled based on selected collection
    [Documentation]  folder2 (fixture): the default collection "Review state" lists the published items
    Open the faceted folder  folder2
    Show the advanced criteria
    The criterion only allows  c2  published
    Select the collection  Creator
    The criterion allows every value  c2

The collection in the URL hash is selected on load
    [Documentation]  folder2 (fixture): "Creator" instead of the default collection "Review state"
    ${uid}=  Path to uid  /${PLONE_SITE_ID}/folder2/collection_wo_review_state
    Go to  ${PLONE_URL}/folder2#c1=${uid}
    The faceted results are loaded
    The collection is selected  Creator
    The page title is  Creator
    Show the advanced criteria
    The criterion allows every value  c2
