from ftw.publisher.core import belongs_to_parent
from ftw.publisher.core.interfaces import IDataCollector
from plone.uuid.interfaces import IUUID
from zope.interface import implementer


@implementer(IDataCollector)
class RemoveChildren(object):
    """The remove children adapter takes care of deleting content which belongs to its parent.
    Content belonging to its parent is not deleted immediately from the receiver, as this may
    change the appearance of the parent (e.g. simplelayout, form gen).
    When the parent is published next, this adapter will make sure that the children, which were
    removed from the sender side, will also be removed from the receiver side.
    """

    def __init__(self, context):
        self.context = context

    def getData(self):
        # Use contentValues in order to have implicit ftw.trash integration.
        return map(IUUID, filter(belongs_to_parent, self.context.contentValues()))

    def setData(self, data, metadata):
        uuids_to_delete = set(self.getData()) - set(data)
        ids_to_delete = []
        for obj in self.context.contentValues():
            if IUUID(obj) in uuids_to_delete:
                ids_to_delete.append(obj.getId())

        if hasattr(self.context, 'manage_immediatelyDeleteObjects'):
            # When ftw.trash is installed, immediately delete the working copy.
            self.context.manage_immediatelyDeleteObjects(ids_to_delete)
        else:
            self.context.manage_delObjects(ids_to_delete)
