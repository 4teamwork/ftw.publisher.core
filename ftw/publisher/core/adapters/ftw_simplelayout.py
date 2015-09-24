from AccessControl.SecurityInfo import ClassSecurityInformation
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.publisher.core.interfaces import IDataCollector
from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from operator import methodcaller
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.interface import implements


marker = object()


def is_sl_contentish(context):
    """This method returns True when the object is considered
    simplelayout contentish.

    Being simplelayout contentish means that the object, usually a block,
    has the same publishing cycle as the parent (page).
    This behavior may be recursive (e.g. files in filelistingblocks).

    An object is considered simplelayout contentish when:
    - it has no workflow and it is a simplelayout block
    - it has no workflow and the parent is a simplelayout block without
    workflow

    When a SL contentish object is deleted on the sender side (redaction),
    it is not directly deleted with a push job, since it is part of the
    content.
    When the SL container (page) is published, it will be removed.
    """

    if IPloneSiteRoot.providedBy(context):
        # Abort recursion when site root reached.
        return False

    if ISimplelayout.providedBy(context):
        # Abort recursion when simplelayout page reached.
        return False

    wftool = getToolByName(context, 'portal_workflow')
    if wftool.getWorkflowsFor(context):
        # The object has a workflow and is therefore not considered sl
        # contentish, since it has its own publishing cycle.
        return False

    if ISimplelayoutBlock.providedBy(context):
        # A block without workflow is always considered sl contentish.
        return True

    # We have an object whithout a workflow.
    # It is considered sl contentish when the parent is sl contentish.
    # It is not considered sl contentish when it is directly in the page.
    parent = aq_parent(aq_inner(context))
    return is_sl_contentish(parent)


class SimplelayoutPageAnnotations(object):
    implements(IDataCollector)
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        return unwrap_persistence(IPageConfiguration(self.context).load())

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        IPageConfiguration(self.context).store(data)


class SimplelayoutBlockAnnotations(object):
    implements(IDataCollector)
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        return unwrap_persistence(IBlockConfiguration(self.context).load())

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        IBlockConfiguration(self.context).store(data)


class RemoveDeletedSLContentishChildren(object):
    implements(IDataCollector)
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        return self._get_contentish_children_uuids()

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        sender_uuids = data
        receiver_uuids = self._get_contentish_children_uuids()
        uuids_to_delete = set(receiver_uuids) - set(sender_uuids)
        children_to_delete = self._get_children_by_uuids(uuids_to_delete)
        self.context.manage_delObjects(map(methodcaller('getId'),
                                           children_to_delete))

    def _get_contentish_children_uuids(self):
        return map(IUUID, filter(is_sl_contentish,
                                 self.context.objectValues()))

    def _get_children_by_uuids(self, uuids):
        return filter(lambda obj: IUUID(obj, marker) in uuids,
                      self.context.objectValues())
