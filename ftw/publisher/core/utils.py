from ZConfig.components.logger import loghandler
import logging
import os.path


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
            errorLogHandler.setFormatter(logging.Formatter(fmt=LOG_FORMAT,
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
    """ Json does not handle encodings, so we need to convert any strings in unicode in
    a way which allows to convert it back on the receiver.
    """
    if additional_encodings:
        encodings = list(EXPECTED_ENCODINGS) + list(additional_encodings)
    else:
        encodings = EXPECTED_ENCODINGS

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

    # lists, tuples, sets
    elif type(value) in (list, tuple, set):
        nval = []
        for sval in value:
            nval.append(decode_for_json(sval))
        if isinstance(value, tuple):
            return tuple(nval)
        if isinstance(value, set):
            return set(nval)
        return nval

    # dicts
    elif isinstance(value, dict):
        nval = {}
        for key, sval in value.items():
            key = decode_for_json(key)
            sval = decode_for_json(sval)
            nval[key] = sval
        return nval

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

    # lists, tuples, sets
    elif type(value) in (list, tuple, set):
        nval = []
        for sval in value:
            nval.append(encode_after_json(sval))
        if isinstance(value, tuple):
            return tuple(nval)
        elif isinstance(value, set):
            return set(nval)
        else:
            return nval

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
