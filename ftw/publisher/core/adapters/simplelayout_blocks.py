from ftw.publisher.core.interfaces import IDataCollector
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.component import adapts
from zope.interface import implements


ATTRIBUTES = ['block_height',
              'image_layout',
              'viewlet_manager',
              'viewname']


class SimplelayoutBlockDataCollector(object):
    implements(IDataCollector)
    adapts(ISimpleLayoutBlock)

    def __init__(self, context):
        self.context = context

    def getData(self):
        config = IBlockConfig(self.context)
        data = {}

        for attr in ATTRIBUTES:
            data[attr] = getattr(config, attr)

        return data

    def setData(self, data, metadata):
        config = IBlockConfig(self.context)

        for attr in ATTRIBUTES:
            setattr(config, attr, data[attr])
