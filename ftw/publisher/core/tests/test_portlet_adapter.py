from BTrees.OOBTree import OOBTree
from ftw.publisher.core import utils
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_EXAMPLE_CONTENT_INTEGRATION
from ftw.publisher.core.utils import IS_PLONE_5
from persistent.mapping import PersistentMapping
from plone.portlet.static import static
from plone.portlets.constants import ASSIGNMENT_SETTINGS_KEY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from unittest2 import TestCase
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
import json



class TestPortletAdapter(TestCase):

    layer = PUBLISHER_EXAMPLE_CONTENT_INTEGRATION

    def test_portlets_adapter_getter(self):
        #getter
        adapter = getAdapter(self.layer['folder1'], IDataCollector,
                             name="portlet_data_adapter")
        getterdata = adapter.getData()

        # we should have the two default portlet manager
        manager_names = [u'plone.rightcolumn', u'plone.leftcolumn']
        self.assertEquals(manager_names, getterdata.keys())

        left = getterdata[u'plone.leftcolumn']
        right = getterdata[u'plone.rightcolumn']

        #check blacklist state
        blacklist_left = getMultiAdapter(
            (self.layer['folder1'], self.layer['left_column']),
            ILocalPortletAssignmentManager)
        blacklist_right = getMultiAdapter(
            (self.layer['folder1'], self.layer['right_column']),
            ILocalPortletAssignmentManager)

        self.assertEquals(
            left['blackliststatus'],
            {'context': blacklist_left.getBlacklistStatus(CONTEXT_CATEGORY),
             'group': blacklist_left.getBlacklistStatus(GROUP_CATEGORY),
             'user': blacklist_left.getBlacklistStatus(USER_CATEGORY),
             'content_type': blacklist_left.getBlacklistStatus(
                    CONTENT_TYPE_CATEGORY)},)

        self.assertEquals(
            right['blackliststatus'],
            {'context': blacklist_right.getBlacklistStatus(CONTEXT_CATEGORY),
             'group': blacklist_right.getBlacklistStatus(GROUP_CATEGORY),
             'user': blacklist_right.getBlacklistStatus(USER_CATEGORY),
             'content_type': blacklist_right.getBlacklistStatus(
                    CONTENT_TYPE_CATEGORY)},)

        #check order of portlets
        self.assertEquals(left['order'].split(','),
                          self.layer['left_portlets']._order)
        self.assertEquals(right['order'].split(','),
                          self.layer['right_portlets']._order)

        #clean up for portlets tests
        del left['blackliststatus']
        del right['blackliststatus']
        del left['order']
        del right['order']

        # check portlets

        # left column

        #static text portlet 1
        title1 = self.layer['left_portlets'].get('title1', False)
        self.assertEquals(bool(title1), True)
        #check given data
        self.assertEquals(title1.header, left['title1']['header'])
        self.assertEquals(title1.text, left['title1']['text'])
        self.assertEquals(title1.omit_border, left['title1']['omit_border'])
        #custom navigation portlet
        navi = self.layer['left_portlets'].get('custom_navigation', False)
        self.assertEquals(bool(navi), True)
        if IS_PLONE_5:
            self.assertEquals(navi.root_uid, left['custom_navigation']['root_uid'])
        else:
            self.assertEquals(navi.root, left['custom_navigation']['root'])
        #check only for given path

        # right portlets

        #static text portlet 2
        title2 = self.layer['right_portlets'].get('title2', False)
        self.assertEquals(bool(title2), True)
        #check given data
        self.assertEquals(title2.header, right['title2']['header'])
        self.assertEquals(title2.text, right['title2']['text'])
        self.assertEquals(title2.omit_border, right['title2']['omit_border'])
        # check collection portlet
        if not IS_PLONE_5:
            collection_portlet = self.layer['right_portlets'].get(
                'collection', False)
            self.assertEquals(bool(collection_portlet), True)
            self.assertEquals(collection_portlet.header,
                              right['collection']['header'])
            self.assertEquals(collection_portlet.limit,
                              right['collection']['limit'])
            self.assertEquals(collection_portlet.random,
                              right['collection']['random'])
            self.assertEquals(collection_portlet.header,
                              right['collection']['header'])
            # more is not necessary, cause we tested enought boolean fields

    def test_portlets_adapter_setter(self):
        #getter
        adapter = getAdapter(self.layer['folder1'], IDataCollector,
                             name="portlet_data_adapter")
        data = adapter.getData()

        #setter - on folder2
        adapter2 = getAdapter(self.layer['folder2'], IDataCollector,
                              name="portlet_data_adapter")
        adapter2.setData(data, metadata=None)

        right_assignments = self.get_right_assignments(self.layer['folder2'])
        left_assignments = self.get_left_assignments(self.layer['folder2'])

        # check right portlets
        title2 = right_assignments.get('title2', False)
        self.assertEquals(bool(title2), True)
        self.assertEquals(title2.header, "Title2")
        self.assertEquals(title2.text, "some text")

        if not IS_PLONE_5:
            collection = right_assignments.get('collection', False)
            self.assertEquals(bool(collection), True)
            self.assertEquals(collection.header, "My collection")
            self.assertEquals(collection.target_collection,
                              "/plone/testing_example_data/atopic")
            self.assertEquals(collection.random, False)

        #check left portlets
        title1 = left_assignments.get('title1', False)
        self.assertEquals(bool(title1), True)
        self.assertEquals(title1.header, "Title1")
        self.assertEquals(title1.text, "some text")

        navi = left_assignments.get('custom_navigation', False)
        self.assertEquals(bool(navi), True)
        if IS_PLONE_5:
            self.assertEquals(navi.root_uid, "/plone/testing_example_data")
        else:
            self.assertEquals(navi.root, "/plone/testing_example_data")


        #check order
        correct_order = ['title2', 'blubb', 'news', 'search']
        if not IS_PLONE_5:
            correct_order.append('collection')
        self.assertEquals(
            correct_order,
            self.layer['right_portlets']._order)

    def test_portlets_adapter_sync(self):
        #getter
        adapter = getAdapter(self.layer['folder1'], IDataCollector,
                             name="portlet_data_adapter")
        data = adapter.getData()

        #setter - on folder2
        adapter2 = getAdapter(self.layer['folder2'], IDataCollector,
                              name="portlet_data_adapter")
        adapter2.setData(data, metadata=None)

        # add another portlet to folder1
        self.layer['left_portlets']['title3'] = static.Assignment(
            header='Title3', text="some text", omit_border=False)

        # now get data again
        adapter3 = getAdapter(
            self.layer['folder1'], IDataCollector,
            name="portlet_data_adapter")
        data2 = adapter3.getData()

        #and sync
        adapter4 = getAdapter(self.layer['folder2'], IDataCollector,
                              name="portlet_data_adapter")
        adapter4.setData(data2, metadata=None)

    def test_portlets_with_settings(self):
        # IPortletAssignmentSettings creates settings in the annotations
        ori_assignment = self.layer['right_portlets'].get('title2', False)
        ori_settings = getAdapter(ori_assignment, IPortletAssignmentSettings)
        ori_settings['foo'] = 'bar'

        # extract the data
        adapter = getAdapter(self.layer['folder1'], IDataCollector,
                             name="portlet_data_adapter")
        getterdata = adapter.getData()
        getterdata = utils.decode_for_json(getterdata)
        jsondata = json.dumps(getterdata)

        # set the data on the folder2
        data = json.loads(jsondata)
        data = utils.encode_after_json(data)
        adapter2 = getAdapter(self.layer['folder2'], IDataCollector,
                              name="portlet_data_adapter")
        adapter2.setData(data, metadata=None)

        # test the assignment settings
        new_assignment = self.layer['right_portlets'].get('title2', False)
        new_settings = getAdapter(new_assignment, IPortletAssignmentSettings)
        self.assertEqual(new_settings['foo'], 'bar')

        assignment_annotations = new_assignment.__annotations__
        self.assertTrue(
            isinstance(assignment_annotations, OOBTree),
            'annotations are not OOBTree but %s' % type(
                assignment_annotations))

        settings = assignment_annotations.get(ASSIGNMENT_SETTINGS_KEY)
        self.assertTrue(
            IPortletAssignmentSettings.providedBy(settings),
            'Portlet settings is not PortletAssignmentSettings but %s' % (
                type(settings)))

    def test_portlet_visibility_settings(self):
        assignment = self.layer['right_portlets'].get('title2', False)
        settings = PersistentMapping({'visible': False})
        IPortletAssignmentSettings(assignment).data = settings

        # get the data
        adapter = getAdapter(self.layer['folder1'], IDataCollector,
                             name="portlet_data_adapter")

        data = adapter.getData()
        jsondata = json.dumps(utils.decode_for_json(data))
        data = utils.encode_after_json(json.loads(jsondata))

        self.assertEqual(
            settings,
            data['plone.rightcolumn']['title2']['settings'])

        # set the data
        adapter2 = getAdapter(self.layer['folder2'], IDataCollector,
                              name="portlet_data_adapter")
        adapter2.setData(data, metadata=None)

        new_assignment = self.layer['right_portlets'].get('title2', False)
        self.assertEqual(
            settings,
            IPortletAssignmentSettings(new_assignment).data)

    def get_right_assignments(self, context):
        return self.get_assignments(context, u'plone.rightcolumn')

    def get_left_assignments(self, context):
        return self.get_assignments(context, u'plone.leftcolumn')

    def get_assignments(self, context, column_name):
        column = getUtility(IPortletManager, name=column_name)
        return getMultiAdapter((context, column), IPortletAssignmentMapping)
