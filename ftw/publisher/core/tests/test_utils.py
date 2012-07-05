from DateTime import DateTime
from datetime import datetime
from ftw.publisher.core import utils
from ftw.testing import MockTestCase
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

    def test_list(self):
        input = ['foo', 'bar']
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

    def test_tuple_becomes_list(self):
        input = ('foo', 'bar')
        output = self.transport(input)
        self.assertEqual(list(output), list(input))
        self.assertNotEqual(type(output), type(input))
        self.assertEqual(type(output), list)

    def test_set_becomes_list(self):
        input = set(['foo', 'bar'])
        output = self.transport(input)
        self.assertEqual(list(output), list(input))
        self.assertNotEqual(type(output), type(input))
        self.assertEqual(type(output), list)

    def test_dict(self):
        input = {'foo': 'bar', 'bar': 'baz'}
        output = self.transport(input)
        self.assertEqual(output, input)
        self.assertEqual(type(output), type(input))

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
