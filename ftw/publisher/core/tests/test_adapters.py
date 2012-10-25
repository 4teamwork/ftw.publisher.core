from DateTime import DateTime
from Products.PloneTestCase.ptc import PloneTestCase
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.tests.layer import Layer
from plone.app.portlets import portlets
from plone.app.portlets.portlets import navigation
from plone.portlet.collection import collection
from plone.portlet.static import static
from plone.portlets.constants import CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getAdapter, getUtility, getMultiAdapter
from zope.interface import alsoProvides, Interface
import unittest


#Dummy Interfaces
class IDummyIface(Interface):
    """This is a dummy interface"""
class IDummyIface2(Interface):
    """This is a dummy interface"""
class IDummyIface3(Interface):
    """This is a dummy interface"""


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
        self.left_portlets['title1'] = static.Assignment(header='Title1', text="some text", omit_border=False)
        self.right_portlets['title2'] = static.Assignment(header='Title2', text="some text", omit_border=False)
        self.right_portlets['blubb'] = static.Assignment(header='blubb', text="some text", omit_border=False)
        self.right_portlets['news'] = portlets.news.Assignment()
        self.right_portlets['search'] = portlets.search.Assignment()
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

        #set dummy interfaces
        alsoProvides(self.testdoc1, IDummyIface)
        alsoProvides(self.testdoc1, IDummyIface2)
        alsoProvides(self.folder2, IDummyIface2)
        alsoProvides(self.folder2, IDummyIface3)


    def test_properties_adapter_getter(self):
        # getter
        adapter = getAdapter(self.testdoc1, IDataCollector, name="properties_data_adapter")
        getterdata = adapter.getData()
        data = [{'type': 'string', 'id': 'title', 'value': u'', 'mode': 'wd'},
                {'type': 'boolean', 'id': 'bool', 'value': True},
                {'type': 'date', 'id': 'date', 'value': '2000/01/01 00:00:00 GMT+1'},
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

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
