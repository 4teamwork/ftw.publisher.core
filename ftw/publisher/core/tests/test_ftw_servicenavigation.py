from ftw.publisher.core.adapters.ftw_servicenavigation import ANNOTATION_KEY
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.publisher.core.utils import decode_for_json
from ftw.publisher.core.utils import encode_after_json
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from unittest2 import TestCase
from zope.annotation import IAnnotations
from zope.component import getAdapter


EXAMPLE_DATA = PersistentMapping({
    'links': PersistentList([
        PersistentMapping({'internal_link': None,
                           'label': u'External Link',
                           'icon': 'heart',
                           'external_url': 'http://www.4teamwork.ch'}),

        PersistentMapping({'internal_link': '/a-page',
                           'label': u'Internal Link',
                           'icon': 'glass',
                           'external_url': None})])})


class TestServiceNavigation(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def test_getData_extracts_data(self):
        annotations = IAnnotations(self.layer['portal'])
        annotations[ANNOTATION_KEY] = EXAMPLE_DATA

        component = getAdapter(self.layer['portal'], IDataCollector,
                               name='ftw.servicenavigation')
        self.assertEqual(EXAMPLE_DATA, component.getData())

    def test_setData_stores_data(self):
        annotations = IAnnotations(self.layer['portal'])
        self.assertIsNone(annotations.get(ANNOTATION_KEY))

        component = getAdapter(self.layer['portal'], IDataCollector,
                               name='ftw.servicenavigation')
        component.setData(EXAMPLE_DATA)
        self.assertEqual(EXAMPLE_DATA, annotations[ANNOTATION_KEY])

    def test_roundtrip_stores_data_persistently(self):
        annotations = IAnnotations(self.layer['portal'])
        component = getAdapter(self.layer['portal'], IDataCollector,
                               name='ftw.servicenavigation')

        annotations[ANNOTATION_KEY] = EXAMPLE_DATA
        wired_data = decode_for_json(component.getData())
        del annotations[ANNOTATION_KEY]

        component.setData(encode_after_json(wired_data))
        data = annotations[ANNOTATION_KEY]
        self.assertEqual(EXAMPLE_DATA, data)
        self.assertIsInstance(data, Persistent)
        self.assertIsInstance(data['links'], Persistent)
