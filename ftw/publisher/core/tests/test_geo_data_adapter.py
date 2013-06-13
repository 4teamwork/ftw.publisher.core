from collective.geo.contentlocations.interfaces import IGeoManager
from collective.geo.geographer.interfaces import IGeoreferenceable
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from zope.annotation import IAttributeAnnotatable
from zope.component import getAdapter
from zope.component import queryAdapter


class TestGeoDataAdapter(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestGeoDataAdapter, self).setUp()

        self.obj = self.providing_stub(
            [IGeoreferenceable, IAttributeAnnotatable])

    def test_component_registered_and_implements_interface(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='geo_data_adapter')
        self.assertTrue(IDataCollector.providedBy(component),
                        'geo Adapter is not registered properly')

    def test_getData_no_coordinates(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='geo_data_adapter')

        self.assertEquals((None, None), component.getData())

    def test_getData_with_coordinates(self):
        self.replay()

        data = 'Point', (0.222, 0.111)
        component = getAdapter(self.obj, IDataCollector,
                               name='geo_data_adapter')

        manager = queryAdapter(self.obj, IGeoManager)
        manager.setCoordinates(*data)

        self.assertEquals(data, component.getData())

    def test_setData(self):
        self.replay()
        setattr(self.obj, 'UID', lambda: 'test-uid')

        data = 'Point', (0.222, 0.111)
        component = getAdapter(self.obj, IDataCollector,
                               name='geo_data_adapter')

        component.setData(data, {})
        manager = queryAdapter(self.obj, IGeoManager)

        self.assertEquals(data, manager.getCoordinates())
