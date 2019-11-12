from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.publisher.core.tests.helpers import add_behaviors
from ftw.publisher.core.utils import IS_PLONE_5
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.testing import staticuid
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from unittest import skipIf
from unittest import TestCase
from zope.component import getAdapter
from zope.component import provideAdapter
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import json


class TestSimplelayoutPageAnnotations(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_data_getter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(
            u'The Block').within(page))

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
        block = create(Builder('sl textblock').titled(
            u'The Block').within(page))
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
        block = create(Builder('sl textblock').titled(
            u'The Block').within(page))

        IBlockConfiguration(block).store({'scale': 'sl_textblock_small'})

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutBlockAnnotations')
        self.assertEquals({'scale': 'sl_textblock_small'},
                          json.loads(json.dumps(component.getData())))

    def test_data_setter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(
            u'The Block').within(page))
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

        if IS_PLONE_5:
            add_behaviors('File', 'plone.app.content.interfaces.INameFromTitle')

    @staticuid('staticuid')
    def test_getter_on_page_returns_contentish_block_uids(self):
        page = create(Builder('sl content page').titled(u'Page'))
        create(Builder('sl textblock').titled(u'TextBlock').within(page))
        create(Builder('sl listingblock').titled(u'Listing').within(page))
        create(Builder('sl content page').titled(u'SubPage').within(page))

        component = getAdapter(page, IDataCollector,
                               name='remove_children')
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
                               name='remove_children')

        self.assertEquals(
            ['textblock', 'listing', 'subpage'], page.objectIds())
        component.setData([u'staticuid00000000000000000000002'], {})
        self.assertEquals(['textblock', 'subpage'], page.objectIds())

    @staticuid('staticuid')
    def test_getter_on_plone_site_returns_contentish_block_uids(self):
        create(Builder('sl textblock').titled(
            u'TextBlock').within(self.portal))
        create(Builder('sl listingblock').titled(
            u'Listing').within(self.portal))
        create(Builder('sl content page').titled(
            u'SubPage').within(self.portal))

        component = getAdapter(self.portal, IDataCollector,
                               name='remove_children')
        self.assertEquals([u'staticuid00000000000000000000001',
                           u'staticuid00000000000000000000002'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_plone_site_deletes_not_listed_blocks(self):
        create(Builder('sl textblock').titled(
            u'TextBlock').within(self.portal))
        create(Builder('sl listingblock').titled(
            u'Listing').within(self.portal))
        create(Builder('sl content page').titled(
            u'SubPage').within(self.portal))

        component = getAdapter(self.portal, IDataCollector,
                               name='remove_children')

        self.assertIn('textblock', self.portal.objectIds())
        self.assertIn('listing', self.portal.objectIds())
        self.assertIn('subpage', self.portal.objectIds())

        component.setData([u'staticuid00000000000000000000001'], {})

        self.assertIn('textblock', self.portal.objectIds())
        self.assertNotIn('listing', self.portal.objectIds())
        self.assertIn('subpage', self.portal.objectIds())

    @staticuid('staticuid')
    def test_getter_on_folderish_block_returns_children_uuids(self):
        page = create(Builder('sl content page').titled(u'Page'))
        listing = create(Builder('sl listingblock').titled(
            u'Listing').within(page))
        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='remove_children')
        self.assertEquals([u'staticuid00000000000000000000003',
                           u'staticuid00000000000000000000004'],
                          json.loads(json.dumps(component.getData())))

    @staticuid('staticuid')
    def test_setter_on_folderish_block_removes_all_childrens_which_are_not_listed(self):
        page = create(Builder('sl content page').titled(u'Page'))
        listing = create(Builder('sl listingblock').titled(
            u'Listing').within(page))

        create(Builder('file').titled(u'Foo').within(listing))
        create(Builder('file').titled(u'Bar').within(listing))

        component = getAdapter(listing, IDataCollector,
                               name='remove_children')
        self.assertEquals(['foo', 'bar'], listing.objectIds())
        component.setData([u'staticuid00000000000000000000003'], {})
        self.assertEquals(['foo'], listing.objectIds())


class TestSimplelayoutBlockLayoutProperty(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        class SampleBlockViewDifferent(BaseBlock):

            def __call__(self):
                return 'OK - different view'

        provideAdapter(SampleBlockViewDifferent,
                       adapts=(Interface, Interface),
                       provides=IBrowserView,
                       name='block_view_different')

    def test_get_layout_property(self):
        page = create(Builder('sl content page').titled(u'Page'))
        block = create(Builder('sl textblock')
                       .titled(u'TextBlock')
                       .within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutBlockProperties')

        self.assertEquals('block_view', component.getData())

    def test_set_layout_property(self):
        page = create(Builder('sl content page').titled(u'Page'))
        block = create(Builder('sl textblock')
                       .titled(u'TextBlock')
                       .within(page))

        component = getAdapter(block, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutBlockProperties')

        component.setData('block_view_different', {})

        properties = queryMultiAdapter((block, block.REQUEST),
                                       IBlockProperties)

        self.assertEquals('block_view_different',
                          properties.get_current_view_name())
