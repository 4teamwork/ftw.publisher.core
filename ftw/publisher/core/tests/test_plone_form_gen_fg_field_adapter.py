from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from persistent.mapping import PersistentMapping
from Products.PloneFormGen.content.fields import HtmlTextField
from Products.PloneFormGen.interfaces import IPloneFormGenField
from zope.component import getAdapter


class TestPloneFormGenFGFieldAdapter(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestPloneFormGenFGFieldAdapter, self).setUp()

        self.obj = self.providing_stub(
            [IPloneFormGenField])
        self.expect(self.obj.UID()).result('some-uid')

    def test_component_registered_and_implements_interface(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        self.assertTrue(
            IDataCollector.providedBy(component),
            'PloneFormGen field adapter is not registered properly')

    def test_getData_without_attribute(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        self.assertEquals(PersistentMapping(), component.getData())

    def test_getData(self):
        field = HtmlTextField()
        field.default = "<div>some html</div>"

        self.expect(self.obj.fgField).result(field)
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        self.assertEquals(
            {'fgField': '<div>some html</div>'},
            component.getData())

    def test_setData_without_attribute(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        component.setData({}, {})

        self.assertFalse(hasattr(self.obj, 'fgField'))

    def test_setData(self):
        field = HtmlTextField()
        field.default = "<div>some html</div>"

        self.expect(self.obj.fgField).result(field)
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        component.setData({'fgField': '<div>new html</div>'}, {})

        self.assertEquals('<div>new html</div>', self.obj.fgField.default)
