from Products.Five.utilities.interfaces import IMarkerInterfaces
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.dottedname.resolve import resolve
from zope.interface import alsoProvides, noLongerProvides
from zope.interface import implements


class InterfaceData(object):
    """returns all properties data
    """

    implements(IDataCollector)
    logger= getLogger()

    def __init__(self,object):
        self.object = object
        self.adapted = IMarkerInterfaces(self.object)

    def getData(self):
        """returns all important data"""
        return self.getInterfaceData()

    def getInterfaceData(self):
        """
        Returns a list of directlyProvided interfaces.
        Example Return: [
            'foo.bar.IDemoInterface',
            ....
            ]

        @return:    list
        @rtype:     list
        """
        return self.adapted.getDirectlyProvidedNames()

    def setData(self, interfacedata, metadata):
        """
        Sets a list of properties on a object.
        Warning: all currently set properties which are not in the
        properties-list wille be removed!

        @param object:      Plone-Object to set the properties on
        @type object:       Plone-Object
        @param properties:  list of propertes. See ftw.publisher.sender.extractor
                            for format details.
        @param type:        list
        @return:            None
        """
        self.logger.info('Updating interface data (UID %s)' %
                (self.object.UID())
        )

        current_ifaces = self.adapted.getDirectlyProvidedNames()

        #delete removed ifaces
        for iface_dotted in current_ifaces:
            iface = resolve(iface_dotted)
            noLongerProvides(self.object, iface)

        for iface_dotted in interfacedata:
            iface = resolve(iface_dotted)
            alsoProvides(self.object, iface)
