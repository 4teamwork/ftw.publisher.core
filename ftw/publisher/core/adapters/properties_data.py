# ftw.publisher.core imports
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core import getLogger

# zope imports
from zope.interface import implements

class PropertiesData(object):
    """returns all properties data
    """
    implements(IDataCollector)
    logger= getLogger()
    
    def __init__(self,object):
        self.object = object
        

    def getData(self):
        """returns all important data"""
        return self.getPropertyData()


    def getPropertyData(self):
        """
        Returns a list of dictonaries each representing a property.
        Example Return: [
            {
                'type' : 'string',
                'id' : 'title',
                'value' : 'test1',
                'mode' : 'wd',
            },
            {
                'type' : 'text',
                'id' : 'blubb',
                'value' : 'asdfsadf
asdf',
            },
        ]

        @return:    list of properties
        @rtype:     list
        """
        properties = []
        for prop in self.object._propertyMap():
            # create a copy (we dont want to change the effective property)
            prop = prop.copy()
            # add the value
            prop['value'] = self.object.getProperty(prop['id'])
            properties.append(prop)
        return properties


    def setData(self, properties, metadata):
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
        self.logger.info('Updating properties (UID %s)' %
                (self.object.UID())
        )
        # we need to cleanup the properties. remove all properties
        # from the object
        propertiesToUpdateOrCreate = [p['id'] for p in properties]
        currentProperties = self.object.propertyIds()
        # delete old properties
        propertiesToDelete = [id for id in currentProperties if id not
                                                in propertiesToUpdateOrCreate]
        self.object.manage_delProperties(propertiesToDelete)
        # get cleaned up list of properties
        currentProperties = self.object.propertyIds()
        # update or create properites
        for prop in properties:
            if prop['id'] in currentProperties:
                # update property if existing ...
                self.object._updateProperty(
                    id = prop['id'],
                    value = prop['value'],
                )
            else:
                # ... otherwise 
                self.object.manage_addProperty(
                    id = prop['id'],
                    value = prop['value'],
                    type = prop['type'],
                )
