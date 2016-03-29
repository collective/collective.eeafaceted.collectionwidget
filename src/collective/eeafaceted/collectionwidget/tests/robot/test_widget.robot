*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

*** Test cases ***

Widget shows no collections or categories when folder is empty
    Make faceted folder
    Go to  ${PLONE_URL}/faceted/configure_faceted.html
    Wait Until Page Contains  Basic search
    Page should contain  Base collections

Widget does not show empty categories
    ${folder}=  Make faceted folder
    ${category}=  Create content  type=Folder  title=News  id=news  container=${folder}
    Go to  ${PLONE_URL}/faceted/configure_faceted.html
    Wait Until Page Contains  Basic search
    Page should contain  Base collections
    # as News is empty, it is not shown
    Element should not be visible  css=div#c1_widget div.title  News
    # create a Collection in the 'news' folder so this category is shown
    ${info}=  Create content  type=Collection  title=Info  id=info  container=${category}
    Click link  Faceted criteria
    Element should be visible  css=div#c1_widget div.title  News
    # the link to the collection is also displayed
    Element should contain  css=div#c1_widget li  Info

Widget shows collections in categories
    [tags]  current
    ${folder}=  Make faceted folder
    ${category}=  Create content  type=Folder  title=News  id=news  container=${folder}
    Create content  type=Collection  title=Info  id=info  container=${category}
    Go to  ${PLONE_URL}/faceted
    Page Should Contain  Info
    Click Element  css=li[title="Info"]
    Wait Until Page Contains Element  css=div.eea-preview-items
    element should contain  css=div.eea-preview-items  Faceted folder

Faceted title matches selected collection
    ${folder}=  Make faceted folder
    Create content  type=Collection  title=Info  id=info  container=${folder}
    Go to  ${PLONE_URL}/faceted/configure_faceted.html
    Wait Until Page Contains  Basic search
    Click Element  css=#c1_widget li
    Go to  ${PLONE_URL}/faceted
    Element should contain  css=h1.documentFirstHeading  Info

Advanced criterion are disabled based on selected collection
    Go to  ${PLONE_URL}/folder2
    Wait Until Element Is Not Visible  css=.faceted-lock-overlay
    Click Element  css=.faceted-sections-buttons-more
    Wait Until Element Is Visible  css=div#c2_widget
    # for the Review state criterion, 6 checkbox are disabled and 1 checked
    ${disabledCount} =  Get Matching Xpath Count  xpath=//*[@id='c2_widget']//input[@disabled]
    Should Be Equal  ${disabledCount}  6
    Click Element  css=li[title="Creator"]
    # all checkboxes for the review state criterion should be available again
    ${disabledCount} =  Get Matching Xpath Count  xpath=//*[@id='c2_widget']//input[@disabled]
    Should Be Equal  ${disabledCount}  0

*** Keywords ***
Suite Setup
    Open test browser
    Enable autologin as  Manager

Make faceted folder
    ${folder}=  Create content  type=Folder  title=Faceted folder  id=faceted
    Go to  ${PLONE_URL}/faceted
    Click element  css=#plone-contentmenu-actions a
    Click element  plone-contentmenu-actions-faceted.enable
    [Return]  ${folder}
