from ftw.publisher.core.utils import getPublisherLogger

def getLogger():
    """
    Returns a logger instance (see python logging module).

    @return logger instance
    """
    return getPublisherLogger('ftw.publisher.receiver')
