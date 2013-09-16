from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core.interfaces import IDataCollector
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from zope import schema
from zope.component import adapts
from zope.interface import implements
import DateTime
import base64
import pkg_resources


try:
    pkg_resources.get_distribution('z3c.relationfield')

except pkg_resources.DistributionNotFound:
    HAS_RELATIONS = False

else:
    HAS_RELATIONS = True
    from z3c.relationfield.interfaces import IRelation
    from z3c.relationfield.interfaces import IRelationChoice
    from z3c.relationfield.interfaces import IRelationList


try:
    pkg_resources.get_distribution('plone.namedfile')

except pkg_resources.DistributionNotFound:
    HAS_NAMEDFILE = False

else:
    HAS_NAMEDFILE = True
    from plone.namedfile.interfaces import INamedFileField
    from plone.namedfile.interfaces import INamedImageField


_marker = object()


class DexterityFieldData(object):
    implements(IDataCollector)
    adapts(IDexterityContent)

    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    def getData(self):
        data = {}

        for schemata in iterSchemata(self.context):
            subdata = {}
            repr = schemata(self.context)
            for name, field in schema.getFieldsInOrder(schemata):
                value = getattr(repr, name, _marker)
                if value == _marker:
                    value = getattr(self.context, name, None)
                value = self.pack(name, field, value)
                subdata[name] = value

            assert schemata.getName() not in data.keys(), \
                'Duplacte behavior names are not supported'

            data[schemata.getName()] = subdata
        return data

    def setData(self, data, metadata):
        """Inserts the field data on self.context
        """

        for schemata in iterSchemata(self.context):
            repr = schemata(self.context)
            subdata = data[schemata.getName()]
            for name, field in schema.getFieldsInOrder(schemata):
                value = subdata[name]
                value = self.unpack(name, field, value)
                if value != _marker:
                    setattr(repr, name, value)

    def pack(self, name, field, value):
        """Packs the field data and makes it ready for transportation with
        json, which does only support basic data types.
        """
        if self._provided_by_one_of(field, [
                schema.interfaces.IDate,
                schema.interfaces.ITime,
                schema.interfaces.IDatetime,
                ]):
            if value:
                return str(value)

        elif HAS_NAMEDFILE and self._provided_by_one_of(field, [
                INamedFileField,
                INamedImageField
                ]):
            if value:
                return {
                    'filename': value.filename,
                    'data': base64.encodestring(value.data),
                    }

        elif HAS_RELATIONS and self._provided_by_one_of(field, (
                IRelation,
                IRelationChoice,
                IRelationList,)):
            # XXX RELATION SUPPORT
            raise NotImplementedError()

        elif self._provided_by_one_of(field, (IRichText,)):
            if value:
                return {'raw': value.raw,
                        'mimeType': value.mimeType,
                        'outputMimeType': value.outputMimeType,
                        'encoding': value.encoding}

        return value

    def unpack(self, name, field, value):
        """Unpacks the value from the basic json types to the objects which
        are stored on the field later.
        """

        if self._provided_by_one_of(field, [
                schema.interfaces.IDate,
                schema.interfaces.ITime,
                schema.interfaces.IDatetime,
                ]):
            if value:
                return DateTime.DateTime(value).asdatetime()

        if HAS_NAMEDFILE and self._provided_by_one_of(
            field, [INamedFileField, INamedImageField]):
            if value and isinstance(value, dict):
                filename = value['filename']
                data = base64.decodestring(value['data'])
                return field._type(data=data, filename=filename)

        if self._provided_by_one_of(field, (IRichText,)):
            if value and isinstance(value, dict):
                return RichTextValue(**value)

        return value

    def _provided_by_one_of(self, obj, ifaces):
        """Checks if at least one interface of the list `ifaces` is provied
        by the `obj`.
        """

        for ifc in ifaces:
            if ifc.providedBy(obj):
                return True
        return False
