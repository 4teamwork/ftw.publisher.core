from ftw.publisher.core import utils
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_EXAMPLE_CONTENT_FIXTURE
from json import dumps
from json import loads
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedFile
from unittest2 import TestCase
from zope.component import getAdapter
from zope.configuration import xmlconfig


class DexterityLayer(PloneSandboxLayer):

    defaultBases = (PUBLISHER_EXAMPLE_CONTENT_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.app.dexterity
        xmlconfig.file('configure.zcml', plone.app.dexterity,
                       context=configurationContext)

        import ftw.publisher.core.tests
        xmlconfig.file('profiles/dexterity.zcml', ftw.publisher.core.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.publisher.core.tests:dexterity')


DX_FIXTURE = DexterityLayer()
DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DX_FIXTURE, ), name="ftw.publisher.core:dexterity integration")


class TestDexterityFieldData(TestCase):

    layer = DX_INTEGRATION_TESTING

    def setUp(self):
        super(TestDexterityFieldData, self).setUp()
        self.portal = self.layer['portal']

    def _get_field_data(self, obj, json=False):
        collector = getAdapter(obj, IDataCollector,
                               name='dx_field_data_adapter')
        data = collector.getData()

        if json:
            data = utils.decode_for_json(data)
            data = dumps(data)

        return data


    def _set_field_data(self, obj, data, metadata=None, json=False):
        collector = getAdapter(obj, IDataCollector,
                               name='dx_field_data_adapter')

        if json:
            data = loads(data)
            data = utils.encode_after_json(data)

        return collector.setData(data, metadata or {})

    def test_dexterity_data_extraction(self):
        obj = createContentInContainer(
            self.portal, 'ExampleDxType', title=u'My Object')

        self.assertEquals({'IBasic': {'description': u'',
                                      'title': u'My Object'},
                           'IFoo': {}},

                          self._get_field_data(obj))

    def test_extract_and_set_data(self):
        foo = createContentInContainer(
            self.portal, 'ExampleDxType', title=u'Foo')
        data = self._get_field_data(foo, json=True)

        bar = createContentInContainer(
            self.portal, 'ExampleDxType', title=u'Bar')

        self.assertEquals('Bar', bar.Title())
        self._set_field_data(bar, data, json=True)
        self.assertEquals('Foo', bar.Title())

    def test_namedfile_files(self):
        filedata = u'**** filedata ****'

        foo = createContentInContainer(
            self.portal, 'DXFile', title=u'Foo')
        foo.file = NamedFile(data=filedata, filename=u'fuu.txt')
        data = self._get_field_data(foo, json=True)

        bar = createContentInContainer(
            self.portal, 'DXFile', title=u'Bar')

        self.assertEquals(bar.file, None)
        self._set_field_data(bar, data, json=True)
        self.assertTrue(bar.file, 'File data missing')

        self.assertEquals(u'fuu.txt', bar.file.filename, 'Filename wrong')