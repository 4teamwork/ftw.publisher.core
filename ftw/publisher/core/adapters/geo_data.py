from AccessControl.SecurityInfo import ClassSecurityInformation
from collective.geo.contentlocations.interfaces import IGeoManager
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.component import queryAdapter
from zope.interface import implements


class GeoData(object):
    """returns geo data
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, obj):
        self.object = obj
        self.manager = queryAdapter(obj, IGeoManager)

    security.declarePrivate('getData')
    def getData(self):
        if self.manager:
            return self.manager.getCoordinates()
        else:
            return None

    security.declarePrivate('setData')
    def setData(self, geodata, metadata):
        self.logger.info('Updating geo data (UID %s)' %
                (self.object.UID())
        )

        if geodata == (None, None):
            self.manager.removeCoordinates()
        else:
            self.manager.setCoordinates(*geodata)
