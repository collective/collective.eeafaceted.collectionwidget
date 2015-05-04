from Products.CMFCore.utils import getToolByName


class CategoriesFromFolder(object):

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        # add an empty category if some collection are defined at the root level
        result = []
        collections = catalog(
            path=dict(query='/'.join(self.context.getPhysicalPath()), depth=1),
            object_provides='plone.app.collection.interfaces.ICollection',
            sort_on="getObjPositionInParent"
        )
        if collections:
            result.append(('', u''))

        folders = catalog(
            path=dict(query='/'.join(self.context.getPhysicalPath()), depth=1),
            portal_type='Folder',
            sort_on="getObjPositionInParent"
        )
        result = result + [(brain.getId, brain.Title) for brain in folders]
        return result
