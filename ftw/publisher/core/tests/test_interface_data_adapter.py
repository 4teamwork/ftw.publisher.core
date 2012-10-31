from Products.Archetypes.interfaces import IBaseObject
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from zope.component import getAdapter
from zope.interface import Interface
from zope.interface import alsoProvides


class IDummy1(Interface):
    pass


def dotted(iface):
    return '.'.join((iface.__module__, iface.__name__))


class TestInterfaceDataAdapter(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered_and_implements_interface(self):
        context = self.providing_stub(IBaseObject)
        self.replay()

        component = getAdapter(context, IDataCollector,
                               name='interface_data_adapter')
        self.assertTrue(IDataCollector.providedBy(component))

    def test_getData(self):
        context = self.providing_stub([IBaseObject, IDummy1])
        self.replay()

        component = getAdapter(context, IDataCollector,
                               name='interface_data_adapter')

        self.assertEquals(component.getData(),
                          [dotted(IBaseObject), dotted(IDummy1)])

    def test_add_interface(self):
        obj = self.create_dummy(UID=lambda: 'testing-uid')
        alsoProvides(obj, IBaseObject)

        self.assertTrue(IBaseObject.providedBy(obj))
        self.assertFalse(IDummy1.providedBy(obj))

        component = getAdapter(obj, IDataCollector,
                               name='interface_data_adapter')
        component.setData([dotted(IBaseObject), dotted(IDummy1)], {})

        self.assertTrue(IBaseObject.providedBy(obj))
        self.assertTrue(IDummy1.providedBy(obj))

    def test_remove_interface(self):
        obj = self.create_dummy(UID=lambda: 'testing-uid')
        alsoProvides(obj, IBaseObject, IDummy1)

        self.assertTrue(IBaseObject.providedBy(obj))
        self.assertTrue(IDummy1.providedBy(obj))

        component = getAdapter(obj, IDataCollector,
                               name='interface_data_adapter')
        component.setData([dotted(IBaseObject)], {})

        self.assertTrue(IBaseObject.providedBy(obj))
        self.assertFalse(IDummy1.providedBy(obj))
