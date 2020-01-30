from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core import belongs_to_parent
from ftw.publisher.core.belongs_to_parent import get_main_obj_belonging_to
from ftw.publisher.core.tests import IntegrationTestCase
from ftw.publisher.core.utils import IS_PLONE_5
from Products.CMFCore.utils import getToolByName
from unittest import skipIf


class TestBelongsToParent(IntegrationTestCase):

    def setUp(self):
        super(TestBelongsToParent, self).setUp()
        self.grant('Contributor')

    def test_plone_site_does_not_belong_to_parent(self):
        self.assertFalse(belongs_to_parent(self.portal))

    def test_folder_does_not_belong_to_parent(self):
        self.set_workflow(Folder=None)
        self.assertFalse(belongs_to_parent(create(Builder('folder'))))

    def test_folders_main_object_is_itself(self):
        self.set_workflow(Folder=None)
        folder = create(Builder('folder'))
        self.assertEquals(get_main_obj_belonging_to(folder), folder)


class TestFTWSimplelayoutBelongsToParent(IntegrationTestCase):

    def setUp(self):
        super(TestFTWSimplelayoutBelongsToParent, self).setUp()
        self.grant('Contributor')
        self.set_workflow({'ftw.simplelayout.ContentPage': 'simple_publication_workflow',
                           'ftw.simplelayout.TextBlock': None,
                           'File': None})

    def test_textblocks_main_obj_is_parent(self):
        self.set_workflow(Folder=None)
        page = create(Builder('sl content page'))
        textblock = create(Builder('sl textblock').within(page))

        self.assertEquals(get_main_obj_belonging_to(textblock), page)

    def test_content_page_does_not_belong_to_parent(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        self.assertFalse(belongs_to_parent(page))

    def test_textblock_belongs_to_parent(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page))
        self.assertTrue(belongs_to_parent(block))

    def test_textblock_with_workflow_does_not_belong_to_parent(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['ftw.simplelayout.TextBlock'], 'plone_workflow')
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page))
        self.assertFalse(belongs_to_parent(block))

    def test_listingblock_belongs_to_parent(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl listingblock').within(page))
        self.assertTrue(belongs_to_parent(block))

    def test_file_in_listingblock_belongs_to_parent(self):
        page = create(Builder('sl content page'))
        listingblock = create(Builder('sl listingblock').within(page))
        document = create(Builder('file').within(listingblock))
        self.assertTrue(belongs_to_parent(document))

    def test_file_with_workflow_in_listingblock_does_not_belong_to_parent(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['File'], 'plone_workflow')
        page = create(Builder('sl content page'))
        listingblock = create(Builder('sl listingblock').within(page))
        document = create(Builder('file').within(listingblock))
        self.assertFalse(belongs_to_parent(document))
