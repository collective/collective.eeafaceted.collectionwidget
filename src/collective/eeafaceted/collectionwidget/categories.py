from Products.CMFCore.utils import getToolByName


class CategoriesAdapter(object):

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.context.getPhysicalPath()), depth=1),
            portal_type='Folder'
        )
        result = [(brain.getId, brain.Title) for brain in brains]
        return result
