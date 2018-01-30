from ftw.publisher.core.tests import test_ftw_contentpage_adapters as sl_adapter
from ftw.publisher.core.utils import IS_PLONE_5
from unittest2 import skipIf

if not IS_PLONE_5:
    from ftw.contentpage.interfaces import ITeaser
    from simplelayout.base.interfaces import IBlockConfig


@skipIf(IS_PLONE_5, 'simplelayout.base is not available for plone 5')
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
