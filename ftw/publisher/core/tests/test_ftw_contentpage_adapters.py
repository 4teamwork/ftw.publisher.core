from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.adapters import simplelayout_blocks
from ftw.publisher.core.adapters.simplelayout_utils import is_sl_contentish
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.testing import MockTestCase
from ftw.testing import staticuid
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.base.interfaces import ISimpleLayoutBlock
from unittest2 import TestCase
from zope.component import getAdapter
import json


class TestContentpageContentish(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_plone_site_is_not_sl_contentish(self):
        self.assertFalse(is_sl_contentish(self.portal))

    def test_content_page_is_not_sl_contentish(self):
        page = create(Builder('content page').titled(u'The Page'))
        self.assertFalse(is_sl_contentish(page))

    def test_textblock_is_contentish(self):
        block = create(Builder('text block')
                       .within(create(Builder('content page'))))
        self.assertTrue(is_sl_contentish(block))

    def test_textblock_with_workflow_is_not_contentish(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['TextBlock'], 'plone_workflow')
        block = create(Builder('text block')
                       .within(create(Builder('content page'))))
        self.assertFalse(is_sl_contentish(block))

    def test_listingblock_is_contentish(self):
        block = create(Builder('listing block')
                       .within(create(Builder('content page'))))
        self.assertTrue(is_sl_contentish(block))

    def test_file_in_listingblock_is_contentish(self):
        document = create(Builder('file')
                          .within(create(Builder('listing block')
                                         .within(create(Builder('content page'))))))
        self.assertTrue(is_sl_contentish(document))

    def test_file_with_workflow_in_listingblock_is_not_contentish(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['File'], 'plone_workflow')
        document = create(Builder('file')
                          .within(create(Builder('listing block')
                                         .within(create(Builder('content page'))))))
        self.assertFalse(is_sl_contentish(document))


class TestRemoveDeletedContentpageSLContentishChildren(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = api.portal.get_tool('portal_types')
        portal_types["TextBlock"].global_allow = True
        portal_types["ListingBlock"].global_allow = True

    @staticuid('staticuid')
    def test_getter_on_page_returns_contentish_block_uids(self):
        page = create(Builder('content page').titled(u'Page'))
        create(Builder('text block').titled(u'TextBlock').within(page))
        create(Builder('listing block').titled(u'Listing').within(page))
        create(Builder('content page').titled(u'SubPage').within(page))

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000002',
                           u'staticuid00000000000000000000003'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_page_deletes_not_listed_blocks(self):
        page = create(Builder('content page').titled(u'Page'))
        create(Builder('text block').titled(u'TextBlock').within(page))
        create(Builder('listing block').titled(u'Listing').within(page))
        create(Builder('content page').titled(u'SubPage').within(page))

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')

        self.assertEquals(['textblock', 'listing', 'subpage'], page.objectIds())
        component.setData([u'staticuid00000000000000000000002'], {})
        self.assertEquals(['textblock', 'subpage'], page.objectIds())

    @staticuid('staticuid')
    def test_getter_on_plone_site_returns_contentish_block_uids(self):
        create(Builder('text block').titled(u'TextBlock').within(self.portal))
        create(Builder('listing block').titled(u'Listing').within(self.portal))
        create(Builder('content page').titled(u'SubPage').within(self.portal))

        component = getAdapter(self.portal, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000001',
                           u'staticuid00000000000000000000002'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_plone_site_deletes_not_listed_blocks(self):
        create(Builder('text block').titled(u'TextBlock').within(self.portal))
        create(Builder('listing block').titled(u'Listing').within(self.portal))
        create(Builder('content page').titled(u'SubPage').within(self.portal))

        component = getAdapter(self.portal, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')

        self.assertIn('textblock', self.portal.objectIds())
        self.assertIn('listing', self.portal.objectIds())
        self.assertIn('subpage', self.portal.objectIds())

        component.setData([u'staticuid00000000000000000000001'], {})

        self.assertIn('textblock', self.portal.objectIds())
        self.assertNotIn('listing', self.portal.objectIds())
        self.assertIn('subpage', self.portal.objectIds())

    @staticuid('staticuid')
    def test_getter_on_textblock_returns_empyt_list(self):
        page = create(Builder('content page').titled(u'Page'))
        block = create(Builder('text block').titled(u'TextBlock').within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_textblock_does_not_break(self):
        page = create(Builder('content page').titled(u'Page'))
        block = create(Builder('text block').titled(u'TextBlock').within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        component.setData([], {})

    @staticuid('staticuid')
    def test_getter_on_folderish_block_returns_children_uuids(self):
        page = create(Builder('content page').titled(u'Page'))
        listing = create(Builder('listing block').titled(u'Listing').within(page))
        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000003',
                           u'staticuid00000000000000000000004'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_folderish_block_removes_all_childrens_which_are_not_listed(self):
        page = create(Builder('content page').titled(u'Page'))
        listing = create(Builder('listing block').titled(u'Listing').within(page))
        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')

        self.assertEquals(['foo', 'bar'], listing.objectIds())
        component.setData([u'staticuid00000000000000000000003'], {})
        self.assertEquals(['foo'], listing.objectIds())


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
