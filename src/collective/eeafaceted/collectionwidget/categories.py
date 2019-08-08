from Products.CMFCore.utils import getToolByName


class CategoriesFromFolder(object):

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        folders = catalog(
            path=dict(query='/'.join(self.context.getPhysicalPath()), depth=1),
            portal_type='Folder',
            sort_on="getObjPositionInParent"
        )
        result = [(brain.UID, brain) for brain in folders]
        return result
