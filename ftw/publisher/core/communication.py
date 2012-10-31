from ftw.publisher.core import states


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
    Decodes the string message from the response containing the state and
    returns a new state object with its message.

    @param data:    String representation of a state
    @type data:     string
    @Return:        state object (ftw.publisher.core.states.CommunicationState)
    """

    classname = data.split('\n')[0]
    message = '\n'.join(data.split('\n')[1:])
    if classname not in dir(states):
        msg = 'Could not find state class: %s (message: %s)' % (
            classname,
            message)
        raise Exception(msg)

    stateClass = getattr(states, classname)
    state = stateClass(message)
    return state
