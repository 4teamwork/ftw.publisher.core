from DateTime import DateTime
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_EXAMPLE_CONTENT_INTEGRATION
from unittest2 import TestCase
from zope.component import getAdapter


class TestPortletAdapter(TestCase):

    layer = PUBLISHER_EXAMPLE_CONTENT_INTEGRATION

    def test_properties_adapter_getter(self):
        # getter
        adapter = getAdapter(self.layer['testdoc1'], IDataCollector,
                             name="properties_data_adapter")
        getterdata = adapter.getData()
        data = [
            {'type': 'string', 'id': 'title', 'value': u'', 'mode': 'wd'},
            {'type': 'boolean', 'id': 'bool', 'value': True},
            {'type': 'date', 'id': 'date',
             'value': '2000/01/01 00:00:00 GMT+1'},
            {'type': 'float', 'id': 'float', 'value': 2.1000000000000001},
            {'type': 'int', 'id': 'int', 'value': 2},
            {'type': 'lines', 'id': 'lines', 'value': ('row1', 'row2')},
            {'type': 'string', 'id': 'string', 'value': 'Hello World!'}]
        self.assertEquals(data, getterdata)

    def test_properties_adapter_setter(self):
        adapter1 = getAdapter(self.layer['testdoc1'], IDataCollector,
                              name="properties_data_adapter")
        data = adapter1.getData()
        # setter
        adapter2 = getAdapter(self.layer['testdoc2'], IDataCollector,
                              name="properties_data_adapter")
        adapter2.setData(data, metadata=None)

        # test boolean
        self.assertEquals(getattr(self.layer['testdoc2'], 'bool'), True)
        # test date
        self.assertEquals(getattr(self.layer['testdoc2'], 'date'),
                          DateTime('2000/01/01'))
        # test float
        self.assertEquals(getattr(self.layer['testdoc2'], 'float'),
                          2.1000000000000001)
        # test int
        self.assertEquals(getattr(self.layer['testdoc2'], 'int'), 2)
        # test lines
        self.assertEquals(getattr(self.layer['testdoc2'], 'lines')[0], 'row1')
        self.assertEquals(getattr(self.layer['testdoc2'], 'lines')[1], 'row2')
        # test string
        self.assertEquals(getattr(self.layer['testdoc2'], 'string'),
                          'Hello World!')

    def test_only_publish_layout_property_on_plone_root(self):
        portal = self.layer['portal']
        portal.setLayout('folder_contents')

        adapter = getAdapter(portal, IDataCollector,
                             name="properties_data_adapter")

        self.assertEquals([{'type': 'string',
                            'id': 'layout',
                            'value': 'folder_contents'}],
                          adapter.getData())

        portal.setLayout('base_view')
        self.assertEquals('base_view', portal.getLayout())

        data = [{'type': 'string',
                 'id': 'layout',
                 'value': 'folder_contents'}]

        cached_title = portal.Title()
        adapter.setData(data, {})

        self.assertEquals(data, adapter.getData())

        # Other properties should be untouched
        self.assertEqual(cached_title, portal.Title())

    def test_remove_layout_property_on_root(self):
        portal = self.layer['portal']
        portal.setLayout('folder_contents')
        portal.manage_delProperties(['layout', ])
        adapter = getAdapter(portal, IDataCollector,
                             name="properties_data_adapter")

        data = adapter.getData()
        self.assertFalse(data, 'Expect an empty list')

        cached_title = portal.Title()
        portal.setLayout('folder_contents')
        adapter.setData(data, {})

        self.assertNotIn('layout',
                         portal.propertyIds(),
                         'Property layout should be removed')

        # Other properties should be untouched
        self.assertEqual(cached_title, portal.Title())

    def test_remove_non_existing_layout_property_on_root(self):
        """
        Removing an non existing layout property on the plone site root
        must not fail.
        """
        portal = self.layer['portal']
        portal.setLayout('folder_contents')
        portal.manage_delProperties(['layout', ])
        adapter = getAdapter(portal, IDataCollector,
                             name="properties_data_adapter")

        data = adapter.getData()
        self.assertFalse(data, 'Expect an empty list')

        cached_title = portal.Title()
        adapter.setData(data, {})

        self.assertNotIn('layout',
                         portal.propertyIds(),
                         'Property layout should be removed')

        # Other properties should be untouched
        self.assertEqual(cached_title, portal.Title())
