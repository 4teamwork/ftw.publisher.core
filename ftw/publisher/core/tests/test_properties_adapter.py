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
        adapter2.setData(data,metadata=None)

        # test boolean
        self.assertEquals(getattr(self.layer['testdoc2'],'bool'), True)
        # test date
        self.assertEquals(getattr(self.layer['testdoc2'],'date'),
                          DateTime('2000/01/01'))
        # test float
        self.assertEquals(getattr(self.layer['testdoc2'],'float'),
                          2.1000000000000001)
        # test int
        self.assertEquals(getattr(self.layer['testdoc2'],'int'), 2)
        # test lines
        self.assertEquals(getattr(self.layer['testdoc2'],'lines')[0], 'row1')
        self.assertEquals(getattr(self.layer['testdoc2'],'lines')[1], 'row2')
        #test string
        self.assertEquals(getattr(self.layer['testdoc2'],'string'),
                          'Hello World!')
