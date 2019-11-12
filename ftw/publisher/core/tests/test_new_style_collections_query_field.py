from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.utils import IS_PLONE_5
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase
from zope.component import getAdapter


QUERY_REPR = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class TestNewStyleCollection(TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        if IS_PLONE_5:
            self.field_data_adapter = 'dx_field_data_adapter'
        else:
            self.field_data_adapter = 'field_data_adapter'

    def test_getData_collection_query(self):
        collection = create(Builder('collection')
                            .titled(u'New style collection')
                            .from_query({'Title': u'Collection Test Page'}))

        component = getAdapter(collection, IDataCollector,
                               name=self.field_data_adapter)

        data = component.getData()
        if IS_PLONE_5:
            self.assertEquals(QUERY_REPR, data['ICollection']['query'])
        else:
            self.assertEquals(QUERY_REPR, data['query'])

    def test_setData_collection_query(self):
        source = create(Builder('collection')
                        .titled(u'New style collection')
                        .from_query({'Title': u'Collection Test Page'}))
        source_component = getAdapter(source, IDataCollector,
                                      name=self.field_data_adapter)

        destination = create(Builder('collection')
                             .titled(u'New style collection 2'))
        destination_component = getAdapter(destination, IDataCollector,
                                           name=self.field_data_adapter)

        destination_component.setData(source_component.getData(),
                                      {'UID': destination.UID()})
        if IS_PLONE_5:
            self.assertEquals(QUERY_REPR, destination.query)
        else:
            self.assertEquals(QUERY_REPR,
                              destination.Schema()['query'].getRaw(destination))
