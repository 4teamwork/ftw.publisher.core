import base64

# publisher.core imports
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core import getLogger

# zope imports
from zope.interface import implements
from zope.component import queryUtility, getMultiAdapter 

# plone.portlets imports
from plone.portlets.interfaces import IPortletManager 
from plone.portlets.interfaces import IPortletAssignmentMapping 
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY, \
                                     CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY
# sys imports
from sys import modules

# OFS imports
from OFS.Image import Image as OFSImage

class PortletsData(object):
    """for plone's defautl portlet data, left and right area 
    """
    implements(IDataCollector)
    logger= getLogger()
    
    def __init__(self,object):
        self.object = object
        

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
        plone_portlet_manager = [u'plone.leftcolumn', u'plone.rightcolumn']
        EXCLUDED_FIELDS = ['__name__', '__parent__']
        # XXX this is a static list, replace by a configlet option
        # the list contains all not serializable portlets (__module__)
        blacklisted_portlets = ['collective.dancing.browser.portlets.channelsubscribe',]
        
        for manager_name in plone_portlet_manager:
            column = queryUtility(IPortletManager, name=manager_name, context=self.object)
            if column is None:
                continue

            #ok we have a portlet manager
            data[manager_name] = {}

            #get blackliststatus
            blacklist = getMultiAdapter((self.object, column), ILocalPortletAssignmentManager)
            data[manager_name]['blackliststatus'] = {}
            blacklistdata = data[manager_name]['blackliststatus']
            blacklistdata[GROUP_CATEGORY] = blacklist.getBlacklistStatus(GROUP_CATEGORY)
            blacklistdata[USER_CATEGORY] = blacklist.getBlacklistStatus(USER_CATEGORY)
            blacklistdata[CONTENT_TYPE_CATEGORY] = blacklist.getBlacklistStatus(CONTENT_TYPE_CATEGORY)
            blacklistdata[CONTEXT_CATEGORY] = blacklist.getBlacklistStatus(CONTEXT_CATEGORY)

            portlets = getMultiAdapter((self.object, column,), IPortletAssignmentMapping, context=self.object)
            
            #portlets order - dicts are unsorted
            data[manager_name]['order'] = portlets._order
            
            for portlet_id in portlets.keys():
                portlet_assignment = portlets[portlet_id]
                #continue if portlet is blacklisted
                if portlet_assignment.__module__ in blacklisted_portlets:
                    continue
                    
                # we habe a portlet
                data[manager_name][portlet_assignment.__name__] = {}
                data[manager_name][portlet_assignment.__name__]['module'] = portlet_assignment.__module__
                #get all data
                for field in portlet_assignment.__dict__.keys():
                    if field not in EXCLUDED_FIELDS:
                        field_value = getattr(portlet_assignment, field, '')
                        # image field - image.portlet integration
                        if isinstance(field_value, OFSImage):
                            # same way as in AT field serializer

                            field_value = {'module':OFSImage.__module__,
                                           'data':base64.encodestring(field_value.data),
                                           'id': field_value.id(),
                                           'title': field_value.title,
                                           'klass_name':OFSImage.__name__}
                        data[manager_name][portlet_assignment.__name__][field] = field_value
        
        return data


    def setData(self, portletsdata, metadata):
        """create or updates portlet informations
        """
        
        for manager_name in portletsdata.keys():
            column = queryUtility(IPortletManager, name=manager_name, context=self.object)
            if column is None:
                continue
            #ok we have a portlet manager
            #get all current assigned portlets
            portlets = getMultiAdapter((self.object, column,), IPortletAssignmentMapping, context=self.object)
            
            #set order
            import pdb; pdb.set_trace( )
            portlets._order = portletsdata[manager_name]['order']
            
            #set blackliststatus
            blacklist = getMultiAdapter((self.object, column), ILocalPortletAssignmentManager)
            blacklistdata = portletsdata[manager_name]['blackliststatus']
            blacklist.setBlacklistStatus(GROUP_CATEGORY,blacklistdata[GROUP_CATEGORY])
            blacklist.setBlacklistStatus(USER_CATEGORY,blacklistdata[USER_CATEGORY])
            blacklist.setBlacklistStatus(CONTENT_TYPE_CATEGORY,blacklistdata[CONTENT_TYPE_CATEGORY])
            blacklist.setBlacklistStatus(CONTEXT_CATEGORY,blacklistdata[CONTEXT_CATEGORY])
            #bit clean up 
            del portletsdata[manager_name]['blackliststatus']

            for portlet_id in portletsdata[manager_name].keys():
                portletfielddata = portletsdata[manager_name][portlet_id]
                
                # XXX remove portlet assignment, because currently
                # we cannot handle edit action on portlet
                if portlet_id in portlets.keys():
                    del portlets[portlet_id]
                    
                if portlet_id in portlets.keys():
                    pass
                    #portlet allready exists we just have to update 
                    # XXX implement edit/update portlet function
                    # XXX for now we just remove them and readd the portlet 
                    #import pdb;pdb.set_trace()
                                    

                    #portlet_assignment = portlets[portlet_id]
                    #for field in portletfielddata.keys():
                    #    break
                        #XXX implement me
                        #should be something like this
                        #assignment.fieldname = field
                    
                else:
                    #we habe to create a new one
                    #get Assignment                    
                    portlet_module = modules[portletfielddata['module']]
                    #prepare data to pass as arguments
                    del portletfielddata['module']
                    
                    #check for dicts
                    for k,v in portletfielddata.items():
                        if isinstance(v, dict):
                            # so we have one, now we have to turn the 
                            # serialized data into an object
                            # this is generic, but currently only in use
                            # by the image portlet
                            klass = modules[v['module']].__dict__[v['klass_name']]
                            imgobj = klass(v['id'],v['title'],base64.decodestring(v['data']))
                            portletfielddata[k] = imgobj
                    
                    portlets[portlet_id] = portlet_module.Assignment(**portletfielddata)

                    # XXX boolean value fix
                    # for some reason boolean types cannpt be passed with **...
                    # use setattr
                    for k,v in portletfielddata.items():
                        if isinstance(v, bool):
                            setattr(portlets[portlet_id], k, v)
