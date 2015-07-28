from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core.interfaces import IDataCollector
from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.interfaces import IPageConfiguration
from zope.interface import implements


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
