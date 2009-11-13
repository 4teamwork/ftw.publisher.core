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


# Superclass

class CommunicationState(Exception):
    """
    Superclass for all states used by publisher packages.
    The CommunicationState class inherits from Exception, because
    we want to be able to "raise" a CommunicationState-object.

        >>> raise CommunicationState('test')
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        states.CommunicationState: test
    """

    def __init__(self, message='', *args, **kwargs):
        """
        Constructs the CommunicationState object. If a message
        is provided, it will be stored for later use.

        @param message:     Status message (optional)
        @type message:      string
        """
        Exception.__init__(self, message, *args, **kwargs)
        self.message = str(message)

    def toString(self):
        """
        Converts a CommunicationState object to a string for printing
        or for sending to a other instance.

            >>> print CommunicationState('Hello World').toString()
            CommunicationState
            Hello World


        @rtype:             string
        @return:            string containing classname and message
        """
        return '\n'.join([
                self.__class__.__name__,
                self.message,
        ])

# Succesful states

class SuccessState(CommunicationState):
    """
    Superclass for all states which indicate that the communication was
    successful.
    """


class ObjectCreatedState(SuccessState):
    """
    Indicates that a new object was created.
    """


class ObjectUpdatedState(SuccessState):
    """
    Indicates that the object was updated successfully.
    """

class ObjectDeletedState(SuccessState):
    """
    Indicates that the object was removed successfully.
    """


# Failed states

class ErrorState(CommunicationState):
    """
    Superclass for all states which indicate that the communication was
    not successful.
    """


class InvalidRequestError(ErrorState):
    """
    Indicates a problem with the submitted request.
    """


class DecodeError(ErrorState):
    """
    Indicates that the decoder was not able to decode the request data to
    json.
    """

class PartialError(ErrorState):
    """
    Indicates that the decoded data was not complete, there were parts missing.
    """

class UnknownActionError(ErrorState):
    """
    An UnknownActionError is raised if the action is not one of the defined
    actions (push, delete).
    """

class UnexpectedError(ErrorState):
    """
    Any exception which is not catched will raise a UnexpectedError containing
    the Exception information.
    """

class ObjectNotFoundError(ErrorState):
    """
    Indicates that the object could not be found.
    """
