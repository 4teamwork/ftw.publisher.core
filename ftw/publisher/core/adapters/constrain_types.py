from plone.app.dexterity.behaviors.constrains import ENABLED
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.component import queryAdapter


class ConstrainTypesDataCollector(object):

    def __init__(self, obj):
        self.constrains = queryAdapter(obj, ISelectableConstrainTypes)

    def getData(self):
        data = {}
        if self.constrains:
            data['mode'] = self.constrains.getConstrainTypesMode()
            if data['mode'] == ENABLED:
                data['locally_allowed'] = self.constrains.getLocallyAllowedTypes()
                data['immediately_addable'] = self.constrains.getImmediatelyAddableTypes()
        return data

    def setData(self, data, metadata):
        if data:
            self.constrains.setConstrainTypesMode(data['mode'])
            if data['mode'] == ENABLED:
                self.constrains.setLocallyAllowedTypes(data['locally_allowed'])
                self.constrains.setImmediatelyAddableTypes(data['immediately_addable'])
