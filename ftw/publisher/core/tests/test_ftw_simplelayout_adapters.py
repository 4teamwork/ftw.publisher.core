from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.adapters.ftw_simplelayout import is_sl_contentish
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.testing import staticuid
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getAdapter
import json


class TestSimplelayoutContentish(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_plone_site_is_not_sl_contentish(self):
        self.assertFalse(is_sl_contentish(self.portal))

    def test_content_page_is_not_sl_contentish(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        self.assertFalse(is_sl_contentish(page))

    def test_textblock_is_contentish(self):
        block = create(Builder('sl textblock')
                       .within(create(Builder('sl content page'))))
        self.assertTrue(is_sl_contentish(block))

    def test_textblock_with_workflow_is_not_contentish(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['ftw.simplelayout.TextBlock'], 'plone_workflow')
        block = create(Builder('sl textblock')
                       .within(create(Builder('sl content page'))))
        self.assertFalse(is_sl_contentish(block))

    def test_listingblock_is_contentish(self):
        block = create(Builder('sl listingblock')
                       .within(create(Builder('sl content page'))))
        self.assertTrue(is_sl_contentish(block))

    def test_file_in_listingblock_is_contentish(self):
        document = create(Builder('file')
                          .within(create(Builder('sl listingblock')
                                         .within(create(Builder('sl content page'))))))
        self.assertTrue(is_sl_contentish(document))

    def test_file_with_workflow_in_listingblock_is_not_contentish(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['File'], 'plone_workflow')
        document = create(Builder('file')
                          .within(create(Builder('sl listingblock')
                                         .within(create(Builder('sl content page'))))))
        self.assertFalse(is_sl_contentish(document))


class TestSimplelayoutPageAnnotations(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_data_getter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))

        IPageConfiguration(page).store(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            })

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutPageAnnotations')
        self.assertEquals(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            },
            json.loads(json.dumps(component.getData())))

    def test_data_setter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))
        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutPageAnnotations')
        component.setData(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            }, {})

        self.assertEquals(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            }, IPageConfiguration(page).load())


class TestSimplelayoutBlockAnnotations(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_data_getter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))

        IBlockConfiguration(block).store({'scale': 'sl_textblock_small'})

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutBlockAnnotations')
        self.assertEquals({'scale': 'sl_textblock_small'},
                          json.loads(json.dumps(component.getData())))

    def test_data_setter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))
        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutBlockAnnotations')
        component.setData({'scale': 'sl_textblock_small'}, {})
        self.assertEquals({'scale': 'sl_textblock_small'},
                          IBlockConfiguration(block).load())


class TestRemoveDeletedSLContentishChildren(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @staticuid('staticuid')
    def test_getter_on_page_returns_contentish_block_uids(self):
        page = create(Builder('sl content page').titled(u'Page'))
        create(Builder('sl textblock').titled(u'TextBlock').within(page))
        create(Builder('sl listingblock').titled(u'Listing').within(page))
        create(Builder('sl content page').titled(u'SubPage').within(page))

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000002',
                           u'staticuid00000000000000000000003'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_page_deletes_not_listed_blocks(self):
        page = create(Builder('sl content page').titled(u'Page'))
        create(Builder('sl textblock').titled(u'TextBlock').within(page))
        create(Builder('sl listingblock').titled(u'Listing').within(page))
        create(Builder('sl content page').titled(u'SubPage').within(page))

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')

        self.assertEquals(['textblock', 'listing', 'subpage'], page.objectIds())
        component.setData([u'staticuid00000000000000000000002'], {})
        self.assertEquals(['textblock', 'subpage'], page.objectIds())

    @staticuid('staticuid')
    def test_getter_on_plone_site_returns_contentish_block_uids(self):
        create(Builder('sl textblock').titled(u'TextBlock').within(self.portal))
        create(Builder('sl listingblock').titled(u'Listing').within(self.portal))
        create(Builder('sl content page').titled(u'SubPage').within(self.portal))

        component = getAdapter(self.portal, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000001',
                           u'staticuid00000000000000000000002'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_plone_site_deletes_not_listed_blocks(self):
        create(Builder('sl textblock').titled(u'TextBlock').within(self.portal))
        create(Builder('sl listingblock').titled(u'Listing').within(self.portal))
        create(Builder('sl content page').titled(u'SubPage').within(self.portal))

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
        page = create(Builder('sl content page').titled(u'Page'))
        block = create(Builder('sl textblock').titled(u'TextBlock').within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_textblock_does_not_break(self):
        page = create(Builder('sl content page').titled(u'Page'))
        block = create(Builder('sl textblock').titled(u'TextBlock').within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        component.setData([], {})

    @staticuid('staticuid')
    def test_getter_on_folderish_block_returns_children_uuids(self):
        page = create(Builder('sl content page').titled(u'Page'))
        listing = create(Builder('sl listingblock').titled(u'Listing').within(page))
        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')
        self.assertEquals([u'staticuid00000000000000000000003',
                           u'staticuid00000000000000000000004'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_folderish_block_removes_all_childrens_which_are_not_listed(self):
        page = create(Builder('sl content page').titled(u'Page'))
        listing = create(Builder('sl listingblock').titled(u'Listing').within(page))
        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='ftw.simplelayout:RemoveDeletedSLContentishChildren')

        self.assertEquals(['foo', 'bar'], listing.objectIds())
        component.setData([u'staticuid00000000000000000000003'], {})
        self.assertEquals(['foo'], listing.objectIds())
