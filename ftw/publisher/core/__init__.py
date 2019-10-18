from ftw.publisher.core.belongs_to_parent import belongs_to_parent
from ftw.publisher.core.utils import getPublisherLogger
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.publisher.core')


def getLogger():
    """
    Returns a logger instance (see python logging module).

    @return logger instance
    """
    return getPublisherLogger('ftw.publisher.core')
