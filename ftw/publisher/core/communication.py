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

import states

def createResponse(state):
    """
    Creates a string message containing the state data which can be parsed
    by parseResponse()-method afterwards.

    @param state:   state object (ftw.publisher.core.states.CommunicationState)
    @type state:    ftw.publisher.core.states.CommunicationState
    @return:        String representation of the state
    """
    if not isinstance(state, states.CommunicationState):
        raise TypeError('Expected CommunicationState instance')
    return state.toString()

def parseResponse(data):
    """
    Decodes the string message from the response containing the state and returns
    a new state object with its message.

    @param data:    String representation of a state
    @type data:     string
    @Return:        state object (ftw.publisher.core.states.CommunicationState)
    """
    classname = data.split('\n')[0]
    message = '\n'.join(data.split('\n')[1:])
    if classname not in dir(states):
        msg = 'Could not find state class: %s (message: %s)' % (classname, message)
        raise Exception(msg)
    stateClass = getattr(states, classname)
    state = stateClass(message)
    return state

