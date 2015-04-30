class DefaultValue(object):
    def __init__(self, context, request, widget):
        self.value = widget.data.default
        # if we  have a default, check if it is still available
        # it could have been deleted or used vocabulary could not contain it
        existingCollectionUids = []
        for group in widget.grouped_vocabulary.values():
            for collection in group:
                existingCollectionUids.append(collection[0])
        if not widget.data.default in existingCollectionUids:
            self.value = existingCollectionUids and existingCollectionUids[0] or None
