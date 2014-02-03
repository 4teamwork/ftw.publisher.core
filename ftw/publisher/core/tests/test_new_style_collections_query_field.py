from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.publisher.core.tests.builders import DEFAULT_QUERY
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase
from zope.component import getAdapter


class TestNewStyleCollection(TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_getData_collection_query(self):
        collection = create(Builder('collection')
                            .titled('New style collection')
                            .with_default_query())

        component = getAdapter(collection, IDataCollector,
                               name='field_data_adapter')

        data = component.getData()
        self.assertEquals(DEFAULT_QUERY, data['query'])

    def test_setData_collection_query(self):
        source = create(Builder('collection')
                        .titled('New style collection')
                        .with_default_query())
        source_component = getAdapter(source, IDataCollector,
                                      name='field_data_adapter')

        destination = create(Builder('collection')
                             .titled('New style collection 2'))
        destination_component = getAdapter(destination, IDataCollector,
                                           name='field_data_adapter')

        destination_component.setData(source_component.getData(),
                                      {'UID': destination.UID()})

        self.assertEquals(DEFAULT_QUERY,
                          destination.Schema()['query'].getRaw(destination))
