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
    Click link  Faceted criteria
    Page should contain  Basic search
    Page should contain  Base collections

Widget does not show empty categories
    ${folder}=  Make faceted folder
    ${category}=  Create content  type=Folder  title=News  id=news  container=${folder}
    Click link  Faceted criteria
    Page should contain  Basic search
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
    Click link  Faceted criteria
    Click Element  css=#c1_widget li
    Go to  ${PLONE_URL}/faceted
    Element should contain  css=h1.documentFirstHeading  Info


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
