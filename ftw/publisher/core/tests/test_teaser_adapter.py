from ftw.contentpage.interfaces import ITeaser
from ftw.publisher.core.tests import test_simplelayout_adapter as sl_adapter
from simplelayout.base.interfaces import IBlockConfig


class TestTeaserDataCollector(sl_adapter.TestSimplelayoutDataCollector):

    def setUp(self):
        super(TestTeaserDataCollector, self).setUp()

        self.obj = self.providing_stub(ITeaser)
        Config = self.stub()
        self.config = self.mock_interface(IBlockConfig)
        self.expect(Config(self.obj)).result(self.config)
        self.mock_adapter(Config, IBlockConfig, [ITeaser])

    def test_getData(self):
        super(TestTeaserDataCollector, self).test_getData()

    def test_setData(self):
        super(TestTeaserDataCollector, self).test_setData()
