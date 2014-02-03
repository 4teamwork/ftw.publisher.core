from AccessControl.SecurityInfo import ClassSecurityInformation
from archetypes.querywidget.field import QueryField
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from OFS.Image import File
from Products.Archetypes.Field import ComputedField
from Products.Archetypes.Field import DateTimeField
from Products.Archetypes.Field import FileField
from zope.interface import implements
import base64
import pkg_resources
import StringIO


try:
    pkg_resources.get_distribution('plone.app.blob')

except pkg_resources.DistributionNotFound:
    HAS_BLOBS = False

else:
    HAS_BLOBS = True
    from plone.app.blob.interfaces import IBlobWrapper


class FieldData(object):
    """returns all field data
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, object):
        self.object = object

    security.declarePrivate('getData')
    def getData(self):
        """returns all important data"""
        return self.getFieldData()

    security.declarePrivate('getFieldData')
    def getFieldData(self):
        """
        Extracts data from the object fields and creates / returns a dictionary
        with the data. Objects are converted to string.
        @return:    dictionary with extracetd data
        @rtype:     dict
        """
        data = {}

        fields = self.object.Schema().fields()

        for field in fields:
            # don't serialize AT ComputedFields
            if isinstance(field, ComputedField):
                continue
            name = field.getName()

            value = field.getRaw(self.object)
            value = self.fieldSerialization(field, value)
            data[name] = value

        return data

    security.declarePrivate('fieldSerialization')
    def fieldSerialization(self, field, value):
        """
        Custom serialization for fields which provide field values that are
        incompatible with json / JSON-standard.
        @param field:   Field-Object from Schema
        @type field:    Field
        @param value:   Return-Value of the Raw-Accessor of the Field on the
        current context
        @type value:    string or stream
        @return:        JSON-optimized value
        @rtype:         string
        """

        if isinstance(field, DateTimeField) and value:
            value = str(value)

        elif HAS_BLOBS and IBlobWrapper.providedBy(value):
            file_ = value.getBlob().open()
            value = {'filename': value.getFilename(),
                     'data': base64.encodestring(file_.read()),
                     'type': 'blob'}
            file_.close()

        elif isinstance(field, FileField) and isinstance(value, File):
            tmp = StringIO.StringIO(value.data)
            tmp.seek(0)
            value = {'filename': value.filename,
                     'data': base64.encodestring(tmp.read())}

        elif isinstance(field, QueryField):
            query = field.getRaw(self.object)
            # Cast "ZPublisher.HTTPRequest.record" instance to dict
            value = [dict(item) for item in query]

        return value

    security.declarePrivate('setData')
    def setData(self, fielddata, metadata):
        """sets all important field data
        """

        # update with new values
        self.logger.info('Updating object values (UID %s)' %
                metadata['UID'])
        fields = self.object.Schema().fields()

        for field in fields:
            fieldname = field.getName()

            # do not update "id" field
            if fieldname == 'id':
                continue

            if fieldname in fielddata.keys():
                field_value = fielddata[fieldname]

                if field.mode == 'r':
                    continue

                field.getMutator(self.object)(field_value)
