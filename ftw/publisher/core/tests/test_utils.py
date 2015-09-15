from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core import utils
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.testing import MockTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import json


class TestEncodeDecodeJson(MockTestCase):

    def transport(self, data, additional_encodings=None):
        """Converts data so that it can be transported and converts it back.
        It should be equally to the original data afterwards.
        """

        transport_data = json.dumps(utils.decode_for_json(data))
        result_data = utils.encode_after_json(json.loads(transport_data))
        return result_data


    def test_string_encodings(self):
        unicodeS = u'\xe4\xeb\xef\xf6\xfc'
        utf8S = unicodeS.encode('utf-8')
        latin1S = unicodeS.encode('latin1')
        iso88591S = unicodeS.encode('iso-8859-1')

        self.assertNotEqual(type(unicodeS), type(utf8S))
        self.assertNotEqual(type(unicodeS), type(latin1S))
        self.assertNotEqual(type(unicodeS), type(iso88591S))

        self.assertNotEqual(utf8S, latin1S)
        self.assertNotEqual(utf8S, iso88591S)

        original = {
            'unicode-data': unicodeS,
            'utf8-data': utf8S,
            'latin1-data': latin1S,
            'iso88591-data': iso88591S}

        result = self.transport(original)
        self.assertEqual(result, original)

    def test_additional_string_encoding(self):
        # test simplified chinese (GB18030)
        data = u'\u6f22\u5b57'.encode('GB18030')

        result = self.transport(data, additional_encodings=['GB18030'])
        self.assertEqual(result, data)

    def test_unicode(self):
        transported = self.transport(u'foo')
        self.assertEqual(u'foo', transported)
        self.assertEqual(unicode, type(transported))

    def test_empty_unicode(self):
        transported = self.transport(u'')
        self.assertEqual(u'', transported)
        self.assertEqual(unicode, type(transported))

    def test_list(self):
        input = ['foo', 'bar']
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_persistent_list(self):
        input = PersistentList(['foo', 'bar'])
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), PersistentList)

    def test_nested_persistent_list(self):
        input = PersistentList(['foo', 'bar', PersistentList(['1', '2'])])
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), PersistentList)

    def test_tuple(self):
        transported = self.transport((1, 2))
        self.assertEqual((1, 2), transported)
        self.assertEqual(tuple, type(transported))

    def test_set(self):
        transported = self.transport({1, 2})
        self.assertEqual({1, 2}, transported)
        self.assertEqual(set, type(transported))

    def test_dict(self):
        input = {'foo': 'bar', 'bar': 'baz'}
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_persistent_mapping(self):
        input = PersistentMapping({'foo': 'bar', 'bar': 'baz'})
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), PersistentMapping)

    def test_nested_persistent_mapping(self):
        input = PersistentMapping(
            {
                'foo': 'bar',
                'bar': PersistentList(['foo', 'bar']),
                'baz': PersistentMapping({'foo': 'bar', 'bar': 'baz'})
            }
        )
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), PersistentMapping)

    def test_integer(self):
        input = 42
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_float(self):
        input = 3.141592654
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_bool(self):
        input = True
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_none(self):
        input = None
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_python_datetime(self):
        input = datetime.now()
        output = self.transport(input)
        self.assertEqual(input, output)
        self.assertEqual(type(input), type(output))

    def test_zope_datetime(self):
        input = DateTime()
        output = self.transport(input)
        self.assertEqual(input, output)
        self.assertEqual(type(input), type(output))


class TestPathFunctions(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    def test_make_path_relative(self):
        self.assertEquals(
            'the-folder/the-page',
            utils.make_path_relative('/plone/the-folder/the-page'))

    def test_get_relative_path(self):
        folder = create(Builder('folder').titled('The Folder'))
        page = create(Builder('page').titled('The Page').within(folder))
        self.assertEquals(
            'the-folder/the-page',
            utils.get_relative_path(page))

    def test_get_obj_by_relative_path(self):
        folder = create(Builder('folder').titled('The Folder'))
        page = create(Builder('page').titled('The Page').within(folder))
        self.assertEquals(
            page,
            utils.get_obj_by_relative_path('the-folder/the-page'))

    def test_get_obj_by_relative_path_returns_None_when_object_missing(self):
        self.assertEquals(
            None,
            utils.get_obj_by_relative_path('the-folder/the-page'))
