from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core.interfaces import IDataCollector
from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from zope.component import queryMultiAdapter
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


class SimplelayoutBlockProperties(object):
    implements(IDataCollector)
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        properties = queryMultiAdapter((self.context, self.context.REQUEST),
                                       IBlockProperties)
        view_name = properties.get_current_view_name()
        return view_name

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        properties = queryMultiAdapter((self.context, self.context.REQUEST),
                                       IBlockProperties)
        properties.set_view(data)
