from ftw.publisher.core.belongs_to_parent import belongs_to_parent  # noqa
from ftw.publisher.core.utils import getPublisherLogger
from zope.i18nmessageid import MessageFactory
import os
import pkg_resources


_ = MessageFactory('ftw.publisher.core')


try:
    pkg_resources.get_distribution('ftw.contentpage')
except pkg_resources.DistributionNotFound:
    pass
else:
    if os.environ.get('FTW_PUBLISHER_DISABLE_FTW_CONTENTPAGE_EXCEPTION', '').lower() != 'true':
        raise ValueError(
            'ftw.publisher.core >= 2.13.0 does no longer support ftw.contentpage. '
            'Please either downgrade ftw.publisher.core or remove ftw.contentpage.')


def getLogger():
    """
    Returns a logger instance (see python logging module).

    @return logger instance
    """
    return getPublisherLogger('ftw.publisher.core')
