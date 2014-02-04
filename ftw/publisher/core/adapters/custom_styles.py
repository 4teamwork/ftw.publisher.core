from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from plonetheme.onegov.interfaces import ICustomStyles
from zope.interface import implements


class CustomStyles(object):

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, obj):
        self.obj = obj

    security.declarePrivate('getData')
    def getData(self):
        return ICustomStyles(self.obj).get_styles()

    security.declarePrivate('setData')
    def setData(self, themedata, metadata):
        ICustomStyles(self.obj).set_styles(themedata)
