from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from Products.PloneFormGen.content.fields import HtmlTextField
from Products.PloneFormGen.interfaces import IPloneFormGenField
from zope.component import getAdapter


class TestPloneFormGenFGFieldAdapter(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestPloneFormGenFGFieldAdapter, self).setUp()

        self.obj = self.providing_stub(
            [IPloneFormGenField])
        self.obj.UID().return_value = 'some-uid'

    def test_component_registered_and_implements_interface(self):
        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        self.assertTrue(
            IDataCollector.providedBy(component),
            'PloneFormGen field adapter is not registered properly')

    def test_getData(self):
        field = HtmlTextField()
        field.default = "<div>some html</div>"

        self.obj.fgField = field
        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        self.assertEquals(
            {'fgField': '<div>some html</div>'},
            component.getData())

    def test_setData(self):
        field = HtmlTextField()
        field.default = "<div>some html</div>"

        self.obj.fgField.side_effect = field
        component = getAdapter(self.obj, IDataCollector,
                               name='plone_form_gen_fg_field_adapter')

        component.setData({'fgField': '<div>new html</div>'}, {})

        self.assertEquals('<div>new html</div>', self.obj.fgField.default)
