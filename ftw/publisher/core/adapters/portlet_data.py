from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from OFS.Image import Image as OFSImage
from plone.portlets.constants import CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from sys import modules
from zope.component import queryUtility, getMultiAdapter
from zope.interface import implements
import base64
import pkg_resources


try:
    pkg_resources.get_distribution('plone.namedfile')
except pkg_resources.DistributionNotFound:
    HAS_NAMEDFILE = False
else:
    from plone.namedfile.interfaces import INamedFile
    HAS_NAMEDFILE = True


class PortletsData(object):
    """for plone's defautl portlet data, left and right area
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, object):
        self.object = object

    security.declarePrivate('getData')
    def getData(self):
        """returns all important data
        data form
        {'column':
        {portlet:
        {key:value}
        }
        .
        .
        .
        .
        {'blackliststatus':
        {category:True},

        {'order':
        ['portlet 1', 'portlet 2']}
        }
        }
        """

        data = {}
        # gets all portlet managers used on this object
        annotations = getattr(self.object, '__annotations__', None)
        if not annotations:
            return data
        if 'plone.portlets.contextassignments' not in annotations:
            return data

        plone_portlet_manager = self.object.__annotations__[
            'plone.portlets.contextassignments'].keys()
        EXCLUDED_FIELDS = ['__name__', '__parent__']
        # XXX this is a static list, replace by a configlet option
        # the list contains all not serializable portlets (__module__)
        blacklisted_portlets = [
            'collective.dancing.browser.portlets.channelsubscribe']

        for manager_name in plone_portlet_manager:
            column = queryUtility(IPortletManager, name=manager_name,
                                  context=self.object)
            if column is None:
                continue

            # ok we have a portlet manager
            data[manager_name] = {}

            # get blackliststatus
            blacklist = getMultiAdapter((self.object, column),
                                        ILocalPortletAssignmentManager)
            data[manager_name]['blackliststatus'] = {}
            blacklistdata = data[manager_name]['blackliststatus']
            blacklistdata[GROUP_CATEGORY] = blacklist.getBlacklistStatus(
                GROUP_CATEGORY)
            blacklistdata[USER_CATEGORY] = blacklist.getBlacklistStatus(
                USER_CATEGORY)

            blacklistdata[CONTENT_TYPE_CATEGORY] = \
                blacklist.getBlacklistStatus(CONTENT_TYPE_CATEGORY)

            blacklistdata[CONTEXT_CATEGORY] = \
                blacklist.getBlacklistStatus(CONTEXT_CATEGORY)

            portlets = getMultiAdapter((self.object, column,),
                                       IPortletAssignmentMapping,
                                       context=self.object)

            # portlets order - dicts are unsorted
            data[manager_name]['order'] = ','.join(portlets._order)

            for portlet_id in portlets.keys():
                portlet_assignment = portlets[portlet_id]
                # continue if portlet is blacklisted
                if portlet_assignment.__module__ in blacklisted_portlets:
                    continue

                # we habe a portlet
                data[manager_name][portlet_assignment.__name__] = {}
                data[manager_name][portlet_assignment.__name__]['module'] = \
                    portlet_assignment.__class__.__module__
                data[manager_name][portlet_assignment.__name__]['assignment_class_name'] = \
                    portlet_assignment.__class__.__name__

                # portlet settings (visibility)
                settings = IPortletAssignmentSettings(portlet_assignment).data
                data[manager_name][portlet_assignment.__name__]['settings'] = settings

                # get all data
                for field in portlet_assignment.__dict__.keys():
                    if field not in EXCLUDED_FIELDS:
                        field_value = getattr(portlet_assignment, field, '')
                        # image field - image.portlet integration
                        if isinstance(field_value, OFSImage):
                            # same way as in AT field serializer

                            field_value = {
                                'module': OFSImage.__module__,
                                'klass_name': OFSImage.__name__,
                                'kwargs': {
                                    'file': base64.encodestring(
                                        field_value.data),
                                    'id': field_value.id(),
                                    'title': field_value.title}}

                        elif (HAS_NAMEDFILE and INamedFile.providedBy(
                                field_value)):
                            klass = type(field_value)
                            field_value = {
                                'module': klass.__module__,
                                'klass_name': klass.__name__,
                                'kwargs': {
                                    'data': base64.encodestring(
                                        field_value.data),
                                    'filename': field_value.filename,
                                    'contentType': field_value.contentType}}

                        data[manager_name][portlet_assignment.__name__][
                            field] = field_value

        return data

    security.declarePrivate('setData')
    def setData(self, portletsdata, metadata):
        """create or updates portlet informations
        """

        for manager_name in portletsdata.keys():
            column = queryUtility(IPortletManager, name=manager_name,
                                  context=self.object)
            if column is None:
                continue
            # ok we have a portlet manager
            # get all current assigned portlets
            portlets = getMultiAdapter((self.object, column,),
                                       IPortletAssignmentMapping,
                                       context=self.object)
            p_ids = [p for p in portlets._data.keys()]
            # get new order
            order = portletsdata[manager_name]['order'] and \
                portletsdata[manager_name]['order'].split(',') or []

            # set blackliststatus
            blacklist = getMultiAdapter((self.object, column),
                                        ILocalPortletAssignmentManager)
            blacklistdata = portletsdata[manager_name]['blackliststatus']
            blacklist.setBlacklistStatus(
                GROUP_CATEGORY, blacklistdata[GROUP_CATEGORY])
            blacklist.setBlacklistStatus(
                USER_CATEGORY, blacklistdata[USER_CATEGORY])
            blacklist.setBlacklistStatus(
                CONTENT_TYPE_CATEGORY, blacklistdata[CONTENT_TYPE_CATEGORY])
            blacklist.setBlacklistStatus(
                CONTEXT_CATEGORY, blacklistdata[CONTEXT_CATEGORY])

            # bit clean up
            del portletsdata[manager_name]['blackliststatus']
            del portletsdata[manager_name]['order']

            # remove all currenlty assigned portlets from manager
            for p_id in p_ids:
                del portlets._data[p_id]

            for portlet_id in portletsdata[manager_name].keys():
                portletfielddata = portletsdata[manager_name][portlet_id]
                # get Assignment
                portlet_module = modules[portletfielddata['module']]
                portlet_class = getattr(portlet_module,
                                        portletfielddata['assignment_class_name'])
                settings = portletfielddata.get('settings', None)
                # prepare data to pass as arguments
                del portletfielddata['module']
                del portletfielddata['assignment_class_name']
                del portletfielddata['settings']

                annotations = portletfielddata.get('__annotations__', None)
                if '__annotations__' in portletfielddata:
                    del portletfielddata['__annotations__']

                # check for dicts
                for k, v in portletfielddata.items():

                    if isinstance(v, dict):
                        # so we have one, now we have to turn the
                        # serialized data into an object
                        # this is generic, but currently only in use
                        # by the image portlet
                        klass = modules[v['module']].__dict__[v['klass_name']]

                        for argname in ('file', 'data'):
                            if argname in v['kwargs']:
                                v['kwargs'][argname] = base64.decodestring(
                                    v['kwargs'][argname])

                        imgobj = klass(**v['kwargs'])
                        portletfielddata[k] = imgobj

                portlets[portlet_id] = portlet_class(
                    **portletfielddata)

                # XXX boolean value fix
                # for some reason boolean types cannpt be passed with **...
                # use setattr
                for k, v in portletfielddata.items():
                    if isinstance(v, bool):
                        setattr(portlets[portlet_id], k, v)

                if annotations:
                    portlets[portlet_id].__annotations__ = annotations

                # portlet settings (visibility)
                portlet_assignment = portlets[portlet_id]
                IPortletAssignmentSettings(portlet_assignment).data = settings

            # set new order afterwards
            portlets._order = order
