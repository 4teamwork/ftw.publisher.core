#
# File:     communication.py
# Author:   Jonas Baumann <j.baumann@4teamwork.ch>
# Modified: 06.03.2009
#
# Copyright (c) 2007 by 4teamwork.ch
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
__author__ = """Jonas Baumann <j.baumann@4teamwork.ch>"""

import os.path
import logging

from ZConfig.components.logger import loghandler

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

