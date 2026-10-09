*** Settings ***
Documentation  collective.eeafaceted.collectionwidget keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.1 syntax (FOR ... END; shared with the Plone 4.3 environment, RF 3.2.2).
...            A folder gets the widgets of testing/default_collection.xml when its faceted navigation is
...            enabled: c0 sorting, c1 collection-link "Base collections" (no default), advanced c2 review
...            state, c3 creator, c4 creation date. Fixture: folder2 is faceted, with the collections
...            "Review state" (published items, default of c1) and "Creator".
...            Paths are relative to the site. Selectors: eea.facetednavigation and this package.
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${WIDGET}  css=#c1_widget
${RESULTS}  css=#faceted-results


*** Keywords ***
Open a manager browser
    Open test browser
    Enable autologin as  Manager

Create a faceted folder
    [Documentation]  Folder "Faceted folder" (/faceted) and its sub-folders (categories), titles @{categories},
    ...              then its faceted navigation: the category vocabulary is cached on the first display.
    [Arguments]  @{categories}
    Create content  type=Folder  id=faceted  title=Faceted folder
    FOR  ${category}  IN  @{categories}
        Create content  type=Folder  container=/${PLONE_SITE_ID}/faceted  title=${category}
    END
    Enable the faceted navigation  faceted

Enable the faceted navigation
    [Documentation]  "Enable faceted navigation" of the Actions menu, which adds the CSRF token
    ...              (Plone 6 asks to confirm a direct GET on @@faceted_subtyper/enable)
    [Arguments]  ${path}
    Go to  ${PLONE_URL}/${path}
    Click the content action  faceted\\.enable
    Wait until page contains element  css=#faceted-form

Create a collection
    [Documentation]  DashboardCollection of the pages, showing its number of items in the widget.
    ...              sort_on: Plone 4 dexterity doesn't fall back to the behavior defaults (AttributeError
    ...              in the widget query). The list type evaluates the value (Bool, list of dicts).
    [Arguments]  ${path}  ${title}
    ${uid}=  Create content  type=DashboardCollection  container=/${PLONE_SITE_ID}/${path}  title=${title}
    ...  sort_on=
    Set field value  ${uid}  sort_reversed  False  list
    Set field value  ${uid}  showNumberOfItems  True  list
    Set field value  ${uid}  query
    ...  [{'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Document']}]  list

Create a page
    [Arguments]  ${path}  ${title}
    Create content  type=Document  container=/${PLONE_SITE_ID}/${path}  title=${title}

Open the faceted folder
    [Arguments]  ${path}
    Go to  ${PLONE_URL}/${path}
    The faceted results are loaded

Open the faceted configuration
    [Documentation]  Waits for the edit widgets, bound once eea.facetednavigation has loaded them
    [Arguments]  ${path}
    Go to  ${PLONE_URL}/${path}/configure_faceted.html
    Wait until page contains element  ${WIDGET}
    Wait for condition  return typeof FacetedEdit !== 'undefined' && FacetedEdit.Widgets.c1 !== undefined

The faceted results are loaded
    Wait until page contains element  ${RESULTS}
    Wait until element is not visible  css=.faceted-lock-overlay

Select the collection
    [Arguments]  ${title}
    Click element  ${WIDGET} li[title="${title}"]
    The faceted results are loaded

Set the default collection
    [Documentation]  In the faceted configuration, a click on a collection makes it the default of the widget.
    ...              A click on the term outside its link: eea.facetednavigation disables the links of the
    ...              widgets there (a click on the label does nothing, Plone 4 too), and the term may be
    ...              covered by its link, depending on the layout.
    [Arguments]  ${path}  ${title}
    Open the faceted configuration  ${path}
    ${term}=  Get WebElement  ${WIDGET} li[title="${title}"]
    Execute javascript  arguments[0].click();  ARGUMENTS  ${term}
    Wait until element contains  css=#faceted-portal-status-message-area  Changes saved

Show the advanced criteria
    Click element  css=.faceted-sections-buttons-more
    Wait until element is visible  css=#c2_widget

The widget lists no collection
    Element should contain  ${WIDGET}  Base collections
    Page should not contain element  ${WIDGET} .category
    Page should not contain element  ${WIDGET} li:not(#c1all)

The widget shows the category
    [Arguments]  ${category}  ${shown}=${True}
    ${locator}=  Set variable  xpath=//*[@id="c1_widget"]//div[@class="category"]/div[@class="title"][normalize-space()="${category}"]
    Run keyword if  ${shown}  Element should be visible  ${locator}
    ...  ELSE  Page should not contain element  ${locator}

The category lists the collection
    [Arguments]  ${category}  ${title}
    Page should contain element
    ...  xpath=//*[@id="c1_widget"]//div[@class="category"][div[@class="title"][normalize-space()="${category}"]]//li[@title="${title}"]

The widget lists the collection
    [Arguments]  ${title}
    Wait until page contains element  ${WIDGET} li[title="${title}"]

The collection shows its number of items
    [Arguments]  ${title}  ${number}
    Element text should be  ${WIDGET} li[title="${title}"] .term-count  ${number}

The collection is selected
    [Arguments]  ${title}
    Wait until page contains element  ${WIDGET} li.faceted-tag-selected[title="${title}"]
    ${selected}=  Get element count  ${WIDGET} li.faceted-tag-selected
    Should be equal as integers  ${selected}  1

The page title is
    [Arguments]  ${title}
    Wait until keyword succeeds  10s  0.5s  Element text should be  ${HEADING}  ${title}

The results list
    [Arguments]  @{titles}
    FOR  ${title}  IN  @{titles}
        Wait until element contains  ${RESULTS}  ${title}
    END

The criterion only allows
    [Documentation]  Checkboxes of the advanced criterion ${cid}: ${value} checked, every other one disabled
    [Arguments]  ${cid}  ${value}
    Checkbox should be selected  css=#${cid}_widget input[value="${value}"]
    Element should be enabled  css=#${cid}_widget input[value="${value}"]
    ${all}=  Get element count  css=#${cid}_widget input[type="checkbox"]
    ${disabled}=  Get element count  css=#${cid}_widget input[type="checkbox"]:disabled
    Should be true  ${all} > 1
    Should be equal as integers  ${disabled}  ${all - 1}

The criterion allows every value
    [Arguments]  ${cid}
    ${disabled}=  Get element count  css=#${cid}_widget input[type="checkbox"]:disabled
    Should be equal as integers  ${disabled}  0

The location is
    [Arguments]  ${url}
    Wait until keyword succeeds  10s  0.5s  Location should be  ${url}

The page URL is
    [Documentation]  Location without its query string and hash (the faceted query is written in the hash)
    [Arguments]  ${url}
    ${location}=  Execute javascript  return window.location.origin + window.location.pathname;
    Should be equal  ${location}  ${url}

The page lists
    [Arguments]  ${title}
    Element should contain  css=#content-core  ${title}

Add a collection of the pages
    [Documentation]  Add menu of the folder at ${path}, query "Type: Page", no sort order
    [Arguments]  ${path}  ${title}
    Open the faceted folder  ${path}
    Open the add menu
    Click the add menu item  dashboardcollection
    Input the title  ${title}
    Add the query criterion  Type
    Select the query value  Page
    Save the add form
