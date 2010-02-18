# base imports
import unittest
import os
from DateTime import DateTime

# zope imports
from zope.component import getAdapter, getUtility, getMultiAdapter


# portlet imports
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.app.portlets import portlets
from plone.portlet.static import static 
from plone.portlet.collection import collection
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY, \
                                     CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY

# publisher imports
from ftw.publisher.core.tests.layer import Layer
from ftw.publisher.core.interfaces import IDataCollector

# Tests
from Products.PloneTestCase.ptc import PloneTestCase 

class TestPublisherAdapters(PloneTestCase): 
    
    layer = Layer
    
    def afterSetUp(self):
        # add some default plone types
        testdoc1id = self.folder.invokeFactory('Document', 'test-doc-1')
        self.testdoc1 = getattr(self.folder,testdoc1id,None)
        folder1id = self.folder.invokeFactory('Folder', 'test-folder-1')
        self.folder1 = getattr(self.folder,folder1id,None)
        folderid2 = self.folder.invokeFactory('Folder', 'test-folder-2')
        self.folder2 = getattr(self.folder,folderid2,None)
        testdoc2id = self.folder1.invokeFactory('Document', 'test-doc-2')
        self.testdoc2 = getattr(self.folder1,testdoc2id,None)
        # create a topic
        topicid = self.folder.manage_addProduct['ATContentTypes'].addATTopic(id='atopic',title='A topic')
        self.topic = getattr(self.folder, topicid, None)



        # set some custom properties
        self.testdoc1.manage_addProperty(id = 'bool', value = True,type = 'boolean')
        self.testdoc1.manage_addProperty(id = 'date', value = '2000/01/01',type = 'date')
        self.testdoc1.manage_addProperty(id = 'float', value = 2.1,type = 'float')
        self.testdoc1.manage_addProperty(id = 'int', value = 2, type = 'int')
        self.testdoc1.manage_addProperty(id = 'lines', value = ('row1', 'row2', ),type = 'lines')
        self.testdoc1.manage_addProperty(id = 'string', value = 'Hello World!',type = 'string')
        
        #put some custom portlets on folder1 - prepare to get portlets from folder 2
        self.left_column = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.folder1)
        self.left_column2 = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.folder2)
        self.right_column = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.folder1)
        self.right_column2 = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.folder2)
        self.left_portlets = getMultiAdapter((self.folder1, self.left_column,), IPortletAssignmentMapping, context=self.folder1)
        self.left_portlets2 = getMultiAdapter((self.folder1, self.left_column,), IPortletAssignmentMapping, context=self.folder2)
        self.right_portlets = getMultiAdapter((self.folder1, self.right_column,), IPortletAssignmentMapping, context=self.folder1) 
        self.right_portlets2 = getMultiAdapter((self.folder1, self.right_column,), IPortletAssignmentMapping, context=self.folder2) 
        
        # static-text-portlets on right and left column
        self.left_portlets['title1'] = static.Assignment(header='Title1',hide=False,text="some text",omit_border=False) 
        self.right_portlets['title2'] = static.Assignment(header='Title2',hide=False,text="some text",omit_border=False)
        
        # collection portlet on the right
        self.right_portlets['collection'] = collection.Assignment(header="My collection", 
                                                             target_collection='/'.join(self.topic.getPhysicalPath()), 
                                                             limit = "5", 
                                                             random = False, 
                                                             show_more = False, 
                                                             show_dates = True, 
                                                             )
        # custom Navigation portlet on the left side
        self.left_portlets['custom_navigation'] = navigation.Assignment(name="custom Navigation", 
                                                                   root='/'.join(self.folder.getPhysicalPath()), 
                                                                   )


        
    def test_properties_adapter_getter(self):
        # getter
        adapter = getAdapter(self.testdoc1, IDataCollector, name="properties_data_adapter")
        getterdata = adapter.getData()
        data = [{'type': 'string', 'id': 'title', 'value': u'', 'mode': 'wd'}, 
                {'type': 'boolean', 'id': 'bool', 'value': True}, 
                {'type': 'date', 'id': 'date', 'value': '2000/01/01'}, 
                {'type': 'float', 'id': 'float', 'value': 2.1000000000000001}, 
                {'type': 'int', 'id': 'int', 'value': 2}, 
                {'type': 'lines', 'id': 'lines', 'value': ('row1', 'row2')}, 
                {'type': 'string', 'id': 'string', 'value': 'Hello World!'}]
        self.assertEquals(data, getterdata)

    def test_properties_adapter_setter(self):
        adapter1 = getAdapter(self.testdoc1, IDataCollector, name="properties_data_adapter")
        data = adapter1.getData()
        # setter
        adapter2 = getAdapter(self.testdoc2, IDataCollector, name="properties_data_adapter")
        adapter2.setData(data,metadata=None)
        
        # test boolean 
        self.assertEquals(getattr(self.testdoc2,'bool'), True)
        # test date
        self.assertEquals(getattr(self.testdoc2,'date'), DateTime('2000/01/01'))
        # test float
        self.assertEquals(getattr(self.testdoc2,'float'), 2.1000000000000001)
        # test int
        self.assertEquals(getattr(self.testdoc2,'int'), 2)
        # test lines
        self.assertEquals(getattr(self.testdoc2,'lines')[0], 'row1')
        self.assertEquals(getattr(self.testdoc2,'lines')[1], 'row2')
        #test string
        self.assertEquals(getattr(self.testdoc2,'string'), 'Hello World!')

    def test_portlets_adapter_getter(self):
        #getter
        adapter = getAdapter(self.folder1, IDataCollector, name="portlet_data_adapter")
        getterdata = adapter.getData()
        
        # we should have the two default portlet manager
        manager_names = [u'plone.rightcolumn', u'plone.leftcolumn']
        self.assertEquals(manager_names, getterdata.keys())
        
        left = getterdata[u'plone.leftcolumn']
        right = getterdata[u'plone.rightcolumn']
        
        #check blacklist state
        blacklist_left = getMultiAdapter((self.folder1, self.left_column), ILocalPortletAssignmentManager)
        blacklist_right = getMultiAdapter((self.folder1, self.right_column), ILocalPortletAssignmentManager)
        self.assertEquals(left['blackliststatus'], {'context': blacklist_left.getBlacklistStatus(CONTEXT_CATEGORY), 
                                                    'group': blacklist_left.getBlacklistStatus(GROUP_CATEGORY), 
                                                    'user': blacklist_left.getBlacklistStatus(USER_CATEGORY), 
                                                    'content_type': blacklist_left.getBlacklistStatus(CONTENT_TYPE_CATEGORY)},)
                                                    
        self.assertEquals(right['blackliststatus'], {'context': blacklist_right.getBlacklistStatus(CONTEXT_CATEGORY), 
                                                    'group': blacklist_right.getBlacklistStatus(GROUP_CATEGORY), 
                                                    'user': blacklist_right.getBlacklistStatus(USER_CATEGORY), 
                                                    'content_type': blacklist_right.getBlacklistStatus(CONTENT_TYPE_CATEGORY)},)
        
        #check order of portlets
        self.assertEquals(left['order'].split(','), self.left_portlets._order)
        self.assertEquals(right['order'].split(','), self.right_portlets._order)
        
        #clean up for portlets tests
        del left['blackliststatus']
        del right['blackliststatus']
        del left['order']
        del right['order']
        

        # check portlets

        # left column

        #static text portlet 1
        title1 = self.left_portlets.get('title1', False)
        self.assertEquals(bool(title1), True)
        #check given data
        self.assertEquals(title1.header, left['title1']['header'])
        self.assertEquals(title1.hide, left['title1']['hide'])
        self.assertEquals(title1.text, left['title1']['text'])
        self.assertEquals(title1.omit_border, left['title1']['omit_border'])        
        #custom navigation portlet
        navi = self.left_portlets.get('custom_navigation', False)
        self.assertEquals(bool(navi), True)
        self.assertEquals(navi.root, left['custom_navigation']['root'])
        #check only for given path

        # right portlets

        #static text portlet 2
        title2 = self.right_portlets.get('title2', False)
        self.assertEquals(bool(title2), True)
        #check given data
        self.assertEquals(title2.header, right['title2']['header'])
        self.assertEquals(title2.hide, right['title2']['hide'])
        self.assertEquals(title2.text, right['title2']['text'])
        self.assertEquals(title2.omit_border, right['title2']['omit_border'])
        # check collection portlet
        collection = self.right_portlets.get('collection', False)
        self.assertEquals(bool(collection), True)
        self.assertEquals(collection.header, right['collection']['header'])
        self.assertEquals(collection.limit, right['collection']['limit'])
        self.assertEquals(collection.random, right['collection']['random'])
        self.assertEquals(collection.header, right['collection']['header'])
        # more is not necessary, cause we tested enought boolean fields

        
    def test_portlets_adapter_setter(self):
        #getter
        adapter = getAdapter(self.folder1, IDataCollector, name="portlet_data_adapter")
        data = adapter.getData()

        #setter - on folder2
        adapter2 = getAdapter(self.folder2, IDataCollector, name="portlet_data_adapter")
        adapter2.setData(data,metadata=None)
        
        # check right portlets
        title2 = self.right_portlets2.get('title2', False)
        self.assertEquals(bool(title2), True)
        self.assertEquals(title2.header, "Title2")
        self.assertEquals(title2.text, "some text")
        self.assertEquals(title2.hide, False)
        
        collection = self.right_portlets2.get('collection', False)
        self.assertEquals(bool(collection), True)
        self.assertEquals(collection.header, "My collection")
        self.assertEquals(collection.target_collection, "/plone/Members/test_user_1_/atopic")
        self.assertEquals(collection.random, False)
        
        #check left portlets
        title1 = self.left_portlets2.get('title1', False)
        self.assertEquals(bool(title1), True)
        self.assertEquals(title1.header, "Title1")
        self.assertEquals(title1.text, "some text")
        self.assertEquals(title1.hide, False)
        
        navi = self.left_portlets2.get('custom_navigation', False)
        self.assertEquals(bool(navi), True)
        self.assertEquals(navi.root, "/plone/Members/test_user_1_")
        

        
        


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)