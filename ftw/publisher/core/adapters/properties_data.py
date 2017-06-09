from AccessControl.SecurityInfo import ClassSecurityInformation
from DateTime import DateTime
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.interface import implements


class PropertiesData(object):
    """returns all properties data
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, object):
        self.object = object

    security.declarePrivate('getData')
    def getData(self):
        """returns all important data"""
        return self.getPropertyData()

    security.declarePrivate('getPropertyData')
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

            if IPloneSiteRoot.providedBy(self.object) and prop['id'] != 'layout':
                continue

            prop['value'] = self.object.getProperty(prop['id'])
            properties.append(prop)

        # property filter for special types
        # ex. date - we have to covert objects to strings
        for p in properties:
            if p['type'] == 'date':
                p['value'] = str(p['value'])

        return properties

    security.declarePrivate('setData')
    def setData(self, properties, metadata):
        """
        Sets a list of properties on a object.
        Warning: all currently set properties which are not in the
        properties-list wille be removed!

        @param object:      Plone-Object to set the properties on
        @type object:       Plone-Object
        @param properties:  list of propertes.
        See ftw.publisher.sender.extractor
        for format details.
        @param type:        list
        @return:            None
        """

        # plone root implementation
        root_path = '/'.join(self.object.getPhysicalPath())
        uid = hasattr(self.object, 'UID') and self.object.UID() or root_path
        self.logger.info('Updating properties (UID %s)' %
                         (uid)
                         )

        # we need to cleanup the properties. remove all properties
        # from the object
        propertiesToUpdateOrCreate = [p['id'] for p in properties]
        currentProperties = self.object.propertyIds()
        # delete old properties
        propertiesToDelete = [id for id in currentProperties if id not
                              in propertiesToUpdateOrCreate]

        if not IPloneSiteRoot.providedBy(self.object):
            self.object.manage_delProperties(propertiesToDelete)
        elif 'layout' in currentProperties:
            # Delete layout property anyway - this supports removing the prop.
            self.object.manage_delProperties(['layout', ])

        # get cleaned up list of properties
        currentProperties = self.object.propertyIds()
        # update or create properites
        for prop in properties:

            # we have to check for some special prop types
            if prop['type'] == 'date':
                val = DateTime(prop['value'])
            else:
                val = prop['value']

            if prop['id'] in currentProperties:
                # update property if existing ...
                try:
                    self.object._updateProperty(
                        id=prop['id'],
                        value=val)
                except AttributeError:
                    self.logger.info(
                        'Could not set property "{0}" on {1}'.format(
                            prop['id'], uid))

            else:
                # ... otherwise
                self.object.manage_addProperty(
                    id=prop['id'],
                    value=val,
                    type=prop['type'])
