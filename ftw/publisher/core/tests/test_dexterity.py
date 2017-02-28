from Acquisition import aq_inner
from ftw.publisher.core import utils
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_EXAMPLE_CONTENT_FIXTURE
from ftw.publisher.core.tests.interfaces import ITextSchema
from json import dumps
from json import loads
from plone.app.relationfield.behavior import IRelatedItems
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from Products.CMFPlone.utils import getFSVersionTuple
from unittest2 import TestCase
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog
from zope.component import getAdapter
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.intid.interfaces import IIntIds


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

    def _get_collector_for(self, obj):
        return getAdapter(obj, IDataCollector,
                          name='dx_field_data_adapter')

    def _get_field_data(self, obj, json=False):
        collector = self._get_collector_for(obj)
        data = collector.getData()

        if json:
            data = utils.decode_for_json(data)
            data = dumps(data)

        return data

    def _set_field_data(self, obj, data, metadata=None, json=False):
        collector = self._get_collector_for(obj)

        if json:
            data = loads(data)
            data = utils.encode_after_json(data)

        return collector.setData(data, metadata or {})

    def test_dexterity_data_extraction(self):
        obj = createContentInContainer(
            self.portal, 'ExampleDxType', title=u'My Object')

        if getFSVersionTuple() >= (4, 3):
            relateditems = ['list', []]
        else:
            relateditems = ['raw', None]

        self.assertEquals({'IBasic': {'description': u'',
                                      'title': u'My Object'},
                           'IFoo': {},
                           'IRelatedItems': {'relatedItems': relateditems}},

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

    def test_named_images(self):
        filedata = u'**** imagedata ****'
        source = createContentInContainer(self.portal, 'DXImage',
                                          title=u'Image')
        source.image = NamedImage(data=filedata, filename=u'picture.jpg')

        data = self._get_field_data(source, json=True)

        target = createContentInContainer(self.portal, 'DXImage')
        self._set_field_data(target, data, json=True)

        self.assertEquals(NamedImage, type(target.image))
        self.assertEquals(u'picture.jpg', target.image.filename)

    def test_richtext_fields(self):
        textdata = u'<b>Text</b>'
        source = createContentInContainer(self.portal, 'DXText',
                                          title=u'Text')
        source.text = ITextSchema['text'].fromUnicode(textdata)

        data = self._get_field_data(source, json=True)

        target = createContentInContainer(self.portal, 'DXText')
        self._set_field_data(target, data, json=True)

        self.assertEquals(RichTextValue, type(target.text))
        self.assertEquals(textdata, target.text.raw)

    def test_relations_when_target_is_available(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        source = createContentInContainer(self.portal, 'ExampleDxType', title=u'Item')
        IRelatedItems(source).relatedItems = [foo]

        data = self._get_field_data(source, json=True)
        target = createContentInContainer(self.portal, 'ExampleDxType')
        self._set_field_data(target, data, json=True)
        self.assertEquals([foo], target.relatedItems)

    def test_relations_with_RelationValue_objects(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        source = createContentInContainer(self.portal, 'ExampleDxType', title=u'Item')
        IRelatedItems(source).relatedItems = [utils.create_relation_for(foo)]

        data = self._get_field_data(source, json=True)
        target = createContentInContainer(self.portal, 'ExampleDxType')
        self._set_field_data(target, data, json=True)
        self.assertEquals(1, len(target.relatedItems),
                          'Relation missing')

        self._set_field_data(target, data, json=True)
        self.assertEquals(1, len(target.relatedItems),
                          'Publishing twice should not add more relations.')

        relation, = target.relatedItems
        self.assertEquals(foo, relation.to_object)

        # Test that the relation is in the catalog.
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)

        target_id = intids.getId(aq_inner(target))
        foo_id = intids.getId(aq_inner(foo))

        relations = tuple(catalog.findRelations({'from_id': target_id, 'to_id': foo_id}))
        self.assertEqual(1, len(relations))
        self.assertEqual(
            target,
            intids.queryObject(relations[0].from_id)
        )
        self.assertEqual(
            foo,
            intids.queryObject(relations[0].to_id)
        )

    def test_relation_is_None(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)
        self.assertEquals(None,
                          collector._unpack_relation(
                              collector._pack_relation(None)))

    def test_relation_is_object(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)
        self.assertEquals(foo,
                          collector._unpack_relation(
                              collector._pack_relation(foo)))

    def test_relation_is_relation_value(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)
        result = collector._unpack_relation(
            collector._pack_relation(
                utils.create_relation_for(foo)))
        self.assertEquals(RelationValue, type(result))
        self.assertEquals(foo, result.to_object)

    def test_relation_is_broken_relation_value(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)
        relation = utils.create_relation_for(foo)
        relation.to_id = None  # break it
        self.assertEquals(None,
                          collector._unpack_relation(
                              collector._pack_relation(relation)))

    def test_list_of_relations(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)

        result = collector._unpack_relation(
            collector._pack_relation(
                [foo,
                 utils.create_relation_for(foo)]))

        self.assertEquals(2, len(result), 'Unexpected length of relations')
        obj, relation = result
        self.assertEquals(foo, obj)
        self.assertEquals(RelationValue, type(relation))
        self.assertEquals(foo, relation.to_object)

    def test_list_of_relations_empty(self):
        foo = createContentInContainer(self.portal, 'ExampleDxType', title=u'Foo')
        collector = self._get_collector_for(foo)

        self.assertEquals([],
                          collector._unpack_relation(
                              collector._pack_relation([])))
