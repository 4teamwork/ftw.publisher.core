from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from datetime import datetime
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.textfield.value import RichTextValue
from plone.portlets.settings import PortletAssignmentSettings
from pytz import timezone
from ZConfig.components.logger import loghandler
from zope.component import getUtility
from zope.component.hooks import getSite
import logging
import os.path
import pkg_resources


"""
@var LOG_FORMAT:        Logging Format (see python logging module)
"""
LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'

"""
@var LOG_DATEFORMAT:    Logging Dateformat (see python logging module)
"""
LOG_DATEFORMAT = '%Y-%m-%dT%H:%M:%S'

"""
@var LOG_FILENAME:      Filename for the log-file to log to.
"""
LOG_FILENAME = 'publisher.log'
ERROR_LOG_FILENAME = 'publisher.error.log'

"""
@var logHandler:        FileHandler instance (see python logging module)
"""
logHandler = None
errorLogHandler = None

ISOFORMAT = '%Y-%m-%dT%H:%M:%S.%f'

EXPECTED_ENCODINGS = (
    'utf8',
    'iso-8859-1',
    'latin1',
    )


def getPublisherLogger(name):
    """
    Creates a python logger which loggs into the custom publisher log.

    @param name:    Name of the logger instance (see python logging module)
    @type name:     string
    @return:        Python logging object
    """

    # get logger
    logger = logging.getLogger(name)
    global logHandler
    if not logHandler:
        # create new handler
        filepath = getLogFilePath(error_log=False)
        if filepath:
            logHandler = logging.FileHandler(filepath)
            # register formatter
            logHandler.setFormatter(logging.Formatter(fmt=LOG_FORMAT,
                                                      datefmt=LOG_DATEFORMAT))

    if logHandler and logHandler not in logger.handlers:
        # register it
        logger.addHandler(logHandler)
    return logger


def getPublisherErrorLogger(name):
    """
    Creates a python logger which loggs into the custom publisher log.

    @param name:    Name of the logger instance (see python logging module)
    @type name:     string
    @return:        Python logging object
    """

    # get logger
    logger = logging.getLogger(name)
    global errorLogHandler
    if not errorLogHandler:
        # create new handler
        filepath = getLogFilePath(error_log=True)
        if filepath:
            errorLogHandler = logging.FileHandler(filepath)
            # register formatter
            errorLogHandler.setFormatter(logging.Formatter(
                    fmt=LOG_FORMAT,
                    datefmt=LOG_DATEFORMAT))

    if errorLogHandler and errorLogHandler not in logger.handlers:
        # register it
        logger.addHandler(errorLogHandler)
    return logger


def getLogFilePath(error_log=False):
    """
    Returns the log file path for the publisher log file.
    Returns None if it cannot guess the default log file path.

    @return:        logfile path or None
    """
    if error_log:
        filename = ERROR_LOG_FILENAME
    else:
        filename = LOG_FILENAME
    # get default log file path
    for handler in logging.root.handlers:
        if isinstance(handler, loghandler.FileHandler):
            path = os.path.dirname(handler.baseFilename)
            return os.path.join(path, filename)
    return None


def decode_for_json(value, additional_encodings=[]):
    """ Json does not handle encodings, so we need to convert any strings
    in unicode in a way which allows to convert it back on the receiver.
    """
    if additional_encodings:
        encodings = list(EXPECTED_ENCODINGS) + list(additional_encodings)
    else:
        encodings = EXPECTED_ENCODINGS

    # OOBTree
    if isinstance(value, OOBTree):
        value = {'publisher-wrapper': True,
                 'type': 'OOBTree',
                 'value': dict(value)}

    # PortletAssignmentSettings
    if isinstance(value, PortletAssignmentSettings):
        value = {'publisher-wrapper': True,
                 'type': 'PortletAssignmentSettings',
                 'value': dict(value.data)}

    # RichTextValue
    if isinstance(value, RichTextValue):
        value = {'publisher-wrapper': True,
                 'type': 'RichTextValue',
                 'value': {'raw': value.raw,
                           'mimeType': value.mimeType,
                           'outputMimeType': value.outputMimeType,
                           'encoding': value.encoding}}

    # unicode
    if isinstance(value, unicode):
        return u'unicode:' + value

    # encoded strings
    elif isinstance(value, str):
        for enc in encodings:
            try:
                return unicode(enc) + u':' + value.decode(enc)
            except UnicodeDecodeError:
                pass
        raise

    # list
    elif isinstance(value, list):
        nval = []
        for sval in value:
            nval.append(decode_for_json(sval))
        return nval

    # PersistentList
    elif isinstance(value, PersistentList):
        return decode_for_json(['PersistentList', list(value)])

    # tuple
    elif isinstance(value, tuple):
        return decode_for_json(['tuple', list(value)])

    # set
    elif isinstance(value, set):
        return decode_for_json(['set', list(value)])

    # dicts
    elif isinstance(value, dict):
        nval = {}
        for key, sval in value.items():
            key = decode_for_json(key)
            sval = decode_for_json(sval)
            nval[key] = sval
        return nval

    # PersistentMapping
    elif isinstance(value, PersistentMapping):
        return decode_for_json(['PersistentMapping', dict(value)])

    # python datetime
    elif isinstance(value, datetime):
        return {'publisher-wrapper': True,
                'type': 'datetime',
                'timetuple': value.timetuple()[:6],
                'tzinfo': value.tzinfo and value.tzinfo.zone}

    # zope datetime
    elif isinstance(value, DateTime):
        return {'publisher-wrapper': True,
                'type': 'DateTime',
                'value': str(value)}

    # others
    else:
        return value


def encode_after_json(value):
    """ Is the opposite of decode_for_json
    """
    # there should not be any encoded strings
    if isinstance(value, str):
        value = unicode(value)

    # unicode
    if isinstance(value, unicode):
        encoding, nval = unicode(value).split(':', 1)
        if encoding == u'unicode':
            return nval

        else:
            return nval.encode(encoding)

    # list, tuple, set
    elif isinstance(value, list):
        new_value = map(encode_after_json, value)
        if len(new_value) == 2 and new_value[0] == 'tuple':
            return tuple(new_value[1])
        elif len(new_value) == 2 and new_value[0] == 'set':
            return set(new_value[1])
        elif len(new_value) == 2 and new_value[0] == 'PersistentList':
            return PersistentList(new_value[1])
        elif len(new_value) == 2 and new_value[0] == 'PersistentMapping':
            return PersistentMapping(new_value[1])
        else:
            return new_value

    # OOBTree
    elif isinstance(value, dict) and \
            value.get('utf8:publisher-wrapper', False) \
            and value.get('utf8:type', None) == 'utf8:OOBTree':
        return OOBTree(value.get('utf8:value'))

    # PortletAssignmentSettings
    elif isinstance(value, dict) and \
            value.get('utf8:publisher-wrapper', False) \
            and value.get('utf8:type', None) == \
            'utf8:PortletAssignmentSettings':
        settings = PortletAssignmentSettings()
        for key, val in value.get('utf8:value').items():
            settings[key] = val
        return settings

    # python datetime
    elif isinstance(value, dict) and \
            value.get('publisher-wrapper', False) \
            and value.get('type', None) == 'datetime':
        if value['tzinfo']:
            tzinfo = timezone(value['tzinfo'])
        else:
            tzinfo = None
        return datetime(*value['timetuple'], tzinfo=tzinfo)

    # zope datetime
    elif isinstance(value, dict) and \
            value.get('publisher-wrapper', False) \
            and value.get('type', None) == 'DateTime':
        return DateTime(value.get('value'))

    elif isinstance(value, dict) and value.get('utf8:publisher-wrapper', False) \
            and value.get('utf8:type', None) == 'utf8:RichTextValue':
        return RichTextValue(**encode_after_json(value['utf8:value']))

    # dicts
    elif isinstance(value, dict):
        nval = {}
        for key, sval in value.items():
            key = encode_after_json(key)
            sval = encode_after_json(sval)
            nval[key] = sval
        return nval

    # other types
    else:
        return value


def make_path_relative(path):
    """Make an absolute path relative to the site root.
    """
    site_path = '/'.join(getSite().getPhysicalPath())
    assert path.startswith(site_path), (
        'The obj path "{0}" does not start with the site path "{1}"'.format(
            path, site_path))

    return path[len(site_path + '/'):]


def get_relative_path(obj):
    """Returns the path to an object relative to the site root.
    """
    site_path = '/'.join(getSite().getPhysicalPath())
    obj_path = '/'.join(obj.getPhysicalPath())
    assert obj_path.startswith(site_path), (
        'The obj path "{0}" does not start with the site path "{1}"'.format(
            obj_path, site_path))

    return obj_path[len(site_path + '/'):]


def get_obj_by_relative_path(relative_path):
    """Returns the object by a path relative to the site root.
    If no object is found, None is returned.
    Bad acquisition lookups are eliminiated.
    """
    site_path = '/'.join(getSite().getPhysicalPath())
    obj_path = '/'.join((site_path, relative_path.strip('/')))
    obj = getSite().restrictedTraverse(obj_path, None)
    if not obj or '/'.join(obj.getPhysicalPath()) != obj_path:
        return None
    return obj


try:
    pkg_resources.get_distribution('z3c.relationfield')

except pkg_resources.DistributionNotFound:
    def create_relation_for(obj):
        # Relations cannot be created since z3c.relationfield is not
        # available. Lets raise an ImportError
        import z3c.relationfield

else:
    from z3c.relationfield import RelationValue
    from zope.intid.interfaces import IIntIds

    def create_relation_for(obj):
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_base(obj))
        return RelationValue(intid)
