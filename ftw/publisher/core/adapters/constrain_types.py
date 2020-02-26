from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.component import queryAdapter


class ConstrainTypesDataCollector(object):

    def __init__(self, obj):
        self.constrains = queryAdapter(obj, ISelectableConstrainTypes)

    def getData(self):
        data = {}
        if self.constrains:
            data['mode'] = self.constrains.getConstrainTypesMode()
            data['locally_allowed'] = self.constrains.getLocallyAllowedTypes()
            data['immediately_addable'] = self.constrains.getImmediatelyAddableTypes()
        return data

    def setData(self, data, metadata):
        if data:
            self.constrains.setConstrainTypesMode(data['mode'])
            self.constrains.setLocallyAllowedTypes(data['locally_allowed'])
            self.constrains.setImmediatelyAddableTypes(data['immediately_addable'])
