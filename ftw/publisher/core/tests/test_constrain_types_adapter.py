from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from Products.CMFPlone.interfaces.constrains import ACQUIRE
from Products.CMFPlone.interfaces.constrains import DISABLED
from Products.CMFPlone.interfaces.constrains import ENABLED
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from unittest import skipUnless
from unittest import TestCase
from ftw.testing import IS_PLONE_5
from zope.component import getAdapter


@skipUnless(IS_PLONE_5, 'Test constrain types adapter for Plone 5')
class TestConstrainTypesAdapter(TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING
    standard_types = [
        'Collection',
        'Document',
        'Folder',
        'Link',
        'File',
        'Image',
        'News Item',
        'Event'
    ]

    def test_data_getter(self):
        self.maxDiff = None
        folder = create(Builder('folder').titled(u'The Folder'))
        constrain_types = ISelectableConstrainTypes(folder)
        constrain_types.setConstrainTypesMode(ENABLED)
        allowed_types = ['Collection', 'Folder']
        immediately_addable_types = ['Collection']
        constrain_types.setLocallyAllowedTypes(allowed_types)
        constrain_types.setImmediatelyAddableTypes(immediately_addable_types)

        adapter = getAdapter(folder, IDataCollector, name='constrain_types_adapter')

        expected_data = {'mode': ENABLED, 'locally_allowed': allowed_types,
                         'immediately_addable': immediately_addable_types}
        self.assertEquals(expected_data, adapter.getData())

        constrain_types.setConstrainTypesMode(DISABLED)
        expected_data = {'mode': DISABLED}
        self.assertEquals(expected_data, adapter.getData())

        constrain_types.setConstrainTypesMode(ACQUIRE)
        expected_data = {'mode': ACQUIRE}
        self.assertEquals(expected_data, adapter.getData())

    def test_data_setter(self):
        folder = create(Builder('folder').titled(u'The Folder'))

        adapter = getAdapter(folder, IDataCollector, name='constrain_types_adapter')
        allowed_types = ['Collection', 'Document', 'Folder']
        immediately_addable_types = ['Collection', 'Folder']

        # Test when mode = 'ENABLED'
        adapter.setData({'mode': ENABLED, 'locally_allowed': allowed_types,
                         'immediately_addable': immediately_addable_types},
                        metadata=None)

        constrain_types = IConstrainTypes(folder)
        self.assertEquals(ENABLED, constrain_types.getConstrainTypesMode())
        self.assertEquals(allowed_types, constrain_types.getLocallyAllowedTypes())
        self.assertEquals(immediately_addable_types, constrain_types.getImmediatelyAddableTypes())

        # Test when mode = 'DISABLED'
        # Results of getLocallyAllowedTypes() and getImmediatelyAddableTypes()
        # are determined by the portal type
        adapter.setData({'mode': DISABLED, 'locally_allowed': allowed_types,
                         'immediately_addable': immediately_addable_types},
                        metadata=None)
        constrain_types = IConstrainTypes(folder)
        self.assertEquals(DISABLED, constrain_types.getConstrainTypesMode())
        self.assertEquals(self.standard_types, constrain_types.getLocallyAllowedTypes())
        self.assertEquals(self.standard_types, constrain_types.getImmediatelyAddableTypes())

        # Test when mode = 'ACQUIRE'
        # Results of getLocallyAllowedTypes() and getImmediatelyAddableTypes()
        # are determined by the parent object
        adapter.setData({'mode': ACQUIRE, 'locally_allowed': allowed_types,
                         'immediately_addable': immediately_addable_types},
                        metadata=None)
        constrain_types = IConstrainTypes(folder)
        self.assertEquals(ACQUIRE, constrain_types.getConstrainTypesMode())
        self.assertEquals(self.standard_types, constrain_types.getLocallyAllowedTypes())
        self.assertEquals(self.standard_types, constrain_types.getImmediatelyAddableTypes())
