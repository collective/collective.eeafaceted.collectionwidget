*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

*** Test cases ***

Widget shows collections in categories
    Make faceted folder
    Page should contain  Base collections
    #Debug
    


*** Keywords ***
Suite Setup
    Open test browser
    Enable autologin as  Manager

Make faceted folder
    Create content  type=Folder  title=Faceted folder  id=faceted
    Go to  ${PLONE_URL}/faceted
    Click element  css=#plone-contentmenu-actions a
    Click element  plone-contentmenu-actions-faceted.enable
    Click link  Faceted criteria
