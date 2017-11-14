from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core import utils
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.publisher.core.tests.behaviors import IDataGridFieldExample
from ftw.publisher.core.utils import create_relation_for
from json import dumps
from json import loads
from plone.dexterity.fti import DexterityFTI
from unittest2 import TestCase
from zope.component import getAdapter


class TestDataGridRelationsAdapter(TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        super(TestDataGridRelationsAdapter, self).setUp()
        self.setup_sample_fti()

        self.content_a = create(Builder('datagrid sample content')
                                .titled(u'refwidget sample content A'))
        self.content_b = create(Builder('datagrid sample content')
                                .titled(u'refwidget sample content B'))

        payload = [{'label': 'First row',
                    'link': create_relation_for(self.content_b)}]
        IDataGridFieldExample(self.content_a).the_data_grid = payload

    def setup_sample_fti(self):
        types_tool = self.layer['portal'].portal_types

        default_behaviors = [
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.content.interfaces.INameFromTitle',
            IDataGridFieldExample.__identifier__
        ]

        fti = DexterityFTI('SampleContent')
        fti.schema = 'ftw.publisher.core.testing.ISampleContentSchema'
        fti.klass = 'ftw.publisher.core.testing.SampleContent'
        fti.behaviors = tuple(default_behaviors)
        fti.default_view = 'view'
        types_tool._setObject('SampleContent', fti)

    def _get_collector_for(self, obj):
        return getAdapter(obj, IDataCollector,
                          name='dx_field_data_adapter')

    def _get_field_data(self, obj):
        collector = self._get_collector_for(obj)
        data = collector.getData()
        data = utils.decode_for_json(data)
        data = dumps(data)
        return data

    def _set_field_data(self, obj, data):
        collector = self._get_collector_for(obj)
        data = loads(data)
        data = utils.encode_after_json(data)
        return collector.setData(data, {})

    def test_extract_and_set_relation_value_in_datagrid(self):
        target = create(Builder('datagrid sample content')
                        .titled(u'target'))

        data = self._get_field_data(self.content_a)
        self._set_field_data(target, data)

        self.assertEquals(
            self.content_b,
            target.the_data_grid[0]['link'].to_object)
