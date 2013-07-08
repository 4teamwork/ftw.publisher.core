from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ZCML_LAYER
from ftw.shop.interfaces import IShopItem
from ftw.shop.interfaces import IVariationConfig
from ftw.testing import MockTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAttributeAnnotatable
from zope.component import getAdapter
from zope.component import queryAdapter
from ftw.publisher.core.adapters.shop_items import make_serializable
from ftw.publisher.core.adapters.shop_items import make_persistent
from ftw.publisher.core.adapters.shop_items import serialize_decimals
from ftw.publisher.core.adapters.shop_items import deserialize_decimals
from decimal import Decimal


TEST_DATA = PersistentMapping(
    {'var-1': PersistentMapping(
        {'active': True,
         'price': '7.00',
         'description': '',
         'skuCode': u'123456'}),
     'var-0': PersistentMapping(
        {'active': True,
         'price': '7.00',
         'description': '',
         'skuCode': u'5555'})
     })


class TestShopItemVariationsAdapter(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestShopItemVariationsAdapter, self).setUp()

        self.obj = self.providing_stub(
            [IShopItem, IVariationConfig, IAttributeAnnotatable])
        self.expect(self.obj.UID()).result('some-uid')

    def test_component_registered_and_implements_interface(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='shop_item_adapter')
        self.assertTrue(IDataCollector.providedBy(component),
                        'ShopItem adapter is not registered properly')

    def test_getData_no_variations(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='shop_item_adapter')

        self.assertEquals(PersistentMapping(), component.getData())

    def test_getData_with_variations(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='shop_item_adapter')

        variation_config = queryAdapter(self.obj, IVariationConfig)
        variation_config.updateVariationConfig(TEST_DATA)

        self.assertEquals(TEST_DATA, component.getData())

    def test_setData(self):
        self.replay()

        component = getAdapter(self.obj, IDataCollector,
                               name='shop_item_adapter')

        component.setData(TEST_DATA, {})
        variation_config = queryAdapter(self.obj, IVariationConfig)

        self.assertEquals(TEST_DATA, variation_config.getVariationDict())


class TestPersistenceSerialization(MockTestCase):

    layer = ZCML_LAYER

    def test_make_serializable(self):
        self.replay()
        data = PersistentMapping(
            {'foo': PersistentList(
                ['bar', PersistentList(
                    [1, 2, 3, 4, 5])
                 ])
             })
        actual = make_serializable(data)
        expected = {'foo': ['bar', [1, 2, 3, 4, 5]]}
        self.assertEquals(actual, expected)

    def test_make_persistent(self):
        self.replay()
        test_data = {'foo': ['bar', [1, 2, 3, 4, 5]]}
        actual = make_persistent(test_data)
        expected = PersistentMapping(
            {'foo': PersistentList(
                ['bar', PersistentList(
                    [1, 2, 3, 4, 5])
                 ])
             })
        self.assertEquals(actual, expected)

    def test_make_persistent_make_serializable_is_idempotent(self):
        self.replay()
        test_data = {'foo': ['bar', [1, 2, 3, 4, 5]]}
        persistent_data = make_persistent(test_data)
        resulting_data = make_serializable(persistent_data)
        self.assertEquals(test_data, resulting_data)


class TestDecimalsSerialization(MockTestCase):

    layer = ZCML_LAYER

    def test_serialized_structure(self):
        self.replay()
        dec = Decimal('1.01')
        result = serialize_decimals(dec)
        self.assertEquals(result['__ftw_publisher_serialized_obj__'], True)
        self.assertEquals(result['__type__'], 'Decimal')
        self.assertEquals(result['value_str'], '1.01')

    def test_values_representable_as_floats(self):
        self.replay()
        value = Decimal('1.00')
        serialized = serialize_decimals(value)
        deserialized = deserialize_decimals(serialized)
        self.assertEquals(deserialized, value)
        self.assertEquals(hash(deserialized), hash(value))

    def test_values_not_representable_as_floats(self):
        self.replay()
        # 1.55 can't be precisely represented as a float, that's why we use
        # this value here
        value = Decimal('1.55')
        serialized = serialize_decimals(value)
        deserialized = deserialize_decimals(serialized)
        self.assertEquals(deserialized, value)
        self.assertEquals(hash(deserialized), hash(value))

    def test_serializing_recurses(self):
        self.replay()
        data = [Decimal('1.55'), {'foo': [Decimal('1.0')]}]
        result = serialize_decimals(data)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[1]['foo'][0], dict)

    def test_deserialize_decimals(self):
        self.replay()
        expected = Decimal('1.55')
        data = {'__ftw_publisher_serialized_obj__': True,
                '__type__': 'Decimal',
                'value_str': '1.55'}
        result = deserialize_decimals(data)
        self.assertEquals(result, expected)
        self.assertEquals(hash(result), hash(expected))

    def test_serialize_deserialize_is_idempotent(self):
        self.replay()
        expected = Decimal('7.50')
        serialized = serialize_decimals(expected)
        deserialized = deserialize_decimals(serialized)
        self.assertEquals(deserialized, expected)
        self.assertEquals(hash(deserialized), hash(expected))
