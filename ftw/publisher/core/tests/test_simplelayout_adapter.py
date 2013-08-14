from ftw.testing import MockTestCase
from ftw.publisher.core.adapters import simplelayout_blocks
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.base.interfaces import ISimpleLayoutBlock


class TestSimplelayoutDataCollector(MockTestCase):

    def setUp(self):
        super(TestSimplelayoutDataCollector, self).setUp()

        self.obj = self.providing_stub(ISimpleLayoutBlock)

        Config = self.stub()
        self.config = self.mock_interface(IBlockConfig)
        self.expect(Config(self.obj)).result(self.config)
        self.mock_adapter(Config, IBlockConfig, [ISimpleLayoutBlock])

    def test_getData(self):
        self.expect(self.config.block_height).result(None)
        self.expect(self.config.image_layout).result('foo')
        self.expect(self.config.viewlet_manager).result('bar')
        self.expect(self.config.viewname).result('baz')

        self.replay()

        collector = simplelayout_blocks.SimplelayoutBlockDataCollector(
            self.obj)

        self.assertEqual(collector.getData(),
                         {'block_height': None,
                          'image_layout': 'foo',
                          'viewlet_manager': 'bar',
                          'viewname': 'baz'})

    def test_setData(self):
        # expect:
        self.config.block_height = None
        self.config.image_layout = 'foo'
        self.config.viewlet_manager = 'bar'
        self.config.viewname = 'baz'

        self.replay()

        input = {'block_height': None,
                 'image_layout': 'foo',
                 'viewlet_manager': 'bar',
                 'viewname': 'baz'}

        collector = simplelayout_blocks.SimplelayoutBlockDataCollector(
            self.obj)
        collector.setData(input, {})
