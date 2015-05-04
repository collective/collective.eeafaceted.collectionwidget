class DefaultValue(object):
    """If we  have a default value, check if it is still available
       it could have been deleted or used vocabulary could not contain it anymore.
       If it is the case, we fall back to first available collection."""
    def __init__(self, context, request, widget):
        self.value = widget.data.default
        existingCollectionUids = []
        for group in widget.grouped_vocabulary.values():
            for collection in group:
                existingCollectionUids.append(collection[0])
        if not widget.data.default in existingCollectionUids:
            self.value = existingCollectionUids and existingCollectionUids[0] or None
