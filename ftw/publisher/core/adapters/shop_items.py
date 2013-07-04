from AccessControl.SecurityInfo import ClassSecurityInformation
from copy import deepcopy
from decimal import Decimal
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from ftw.shop.interfaces import IVariationConfig
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.component import queryAdapter
from zope.interface import implements


def make_serializable(value):
    """Recursively converts all instances of PersistentMapping and
    PersistentList in a nested value to regular dicts respectively lists so
    the value is ready for serialization.
    """
    if isinstance(value, PersistentMapping):
        retval = dict()
        for key in value:
            retval[key] = make_serializable(value[key])
    elif isinstance(value, PersistentList):
        retval = list()
        for item in value:
            retval.append(make_serializable(item))
    else:
        retval = value
    return retval


def make_persistent(value):
    """Counterpart to make_serializable().
    Recursively turns all dicts and lists into PersistentMappings respectively
    PersistentLists.
    """
    if isinstance(value, dict):
        retval = PersistentMapping()
        retval.update(value)
    elif isinstance(value, list):
        retval = PersistentList()
        for item in value:
            retval.append(item)
    else:
        retval = value
    return retval


def serialize_decimals(value):
    """Recursively turns instances of decimal.Decimal into serializable dict
    representations that can be deserialized by deserialize_decimals().
    """
    if isinstance(value, dict) or isinstance(value, PersistentMapping):
        retval = value.__class__()
        for key in value:
            retval[key] = serialize_decimals(value[key])
    elif isinstance(value, list) or isinstance(value, PersistentList):
        retval = value.__class__()
        for item in value:
            retval.append(serialize_decimals(item))
    elif isinstance(value, Decimal):
        retval = dict()
        retval['__ftw_publisher_serialized_obj__'] = True
        retval['__type__'] = 'Decimal'
        retval['value_str'] = str(value)
    else:
        retval = value
    return retval


def deserialize_decimals(value):
    """Counterpart to serialize_decimals().
    Recursively turns dict representations of decimals back into
    decimal.Decimal objects.
    """
    if isinstance(value, dict) and '__ftw_publisher_serialized_obj__' in value:
        if value.get('__type__') == 'Decimal':
            retval = Decimal(value.get('value_str'))
    elif isinstance(value, dict) or isinstance(value, PersistentMapping):
        retval = value.__class__()
        for key in value:
            retval[key] = deserialize_decimals(value[key])
    elif isinstance(value, list) or isinstance(value, PersistentList):
        retval = value.__class__()
        for item in value:
            retval.append(deserialize_decimals(item))
    else:
        retval = value
    return retval


class ShopItemVariations(object):
    """DataCollector adapter for Shop Item Variations.
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, obj):
        self.object = obj

    security.declarePrivate('getData')
    def getData(self):
        variations_config = queryAdapter(self.object, IVariationConfig)
        if variations_config:
            data = deepcopy(variations_config.getVariationDict())
        else:
            data = PersistentMapping()
        data = make_serializable(data)
        data = serialize_decimals(data)
        return data

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        variations_config = queryAdapter(self.object, IVariationConfig)
        self.logger.info('Updating variations config (UID %s)' %
                         (self.object.UID()))

        data = make_persistent(data)
        data = deserialize_decimals(data)
        if data in ({}, PersistentMapping()):
            variations_config.purge_dict()
        else:
            variations_config.updateVariationConfig(data)
