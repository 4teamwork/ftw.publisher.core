import base64
import StringIO

# plone imports
from Products.Archetypes.Field import DateTimeField
from Products.Archetypes.Field import FileField
from Products.Archetypes.Field import ComputedField

# publisher.core imports
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core import getLogger

# zope imports
from OFS.Image import File
from zope.interface import implements
from zope.component import queryAdapter

#make archetype.schemaextender aware
HAS_AT_SCHEMAEXTENDER = False
try:
    from archetypes.schemaextender.interfaces import ISchemaExtender
    HAS_AT_SCHEMAEXTENDER = True
except ImportError:
    pass


class FieldData(object):
    """returns all field data
    """
    implements(IDataCollector)
    logger = getLogger()
    
    def __init__(self,object):
        self.object = object
        

    def getData(self):
        """returns all important data"""
        return self.getFieldData()
        

    def getFieldData(self):
        """
        Extracts data from the object fields and creates / returns a dictionary with
        the data. Objects are converted to string.
        @return:    dictionary with extracetd data
        @rtype:     dict
        """
        data = {}

        fields = self.object.schema.fields()
        if HAS_AT_SCHEMAEXTENDER and queryAdapter(self.object, ISchemaExtender):
            fields += ISchemaExtender(self.object).getFields()        
            
        for field in fields:
            # don't serialize AT ComputedFields
            if isinstance(field, ComputedField):
                continue
            name = field.getName()
            
            value = field.getRaw(self.object)
            value = self.fieldSerialization(field, value)
            data[name] = value
        
        return data

    def fieldSerialization(self, field, value):
        """
        Custom serialization for fields which provide field values that are incompatible
        with simplejson / JSON-standard.
        @param field:   Field-Object from Schema
        @type field:    Field
        @param value:   Return-Value of the Raw-Accessor of the Field on the current context
        @type value:    string or stream
        @return:        JSON-optimized value
        @rtype:         string
        """
        # DateField : returns a DateTime-Object as value. We cast it to string and it
        #   looks like '2010-05-31 13:06:01.925652'
        if isinstance(field, DateTimeField) and value:
            value = str(value)
        # FileField : returns a File-Object, but TextField is a FileField too, so we
        # have to detect the type of value. Binary data must be encoded with base64
        elif isinstance(field, FileField):
            if isinstance(value, File):
                # we have to convert our dara first into StringIO
                # otherwise base64.encodestring sometimes cut's some data off
                tmp = StringIO.StringIO(value.data)
                tmp.seek(0)
                value = {
                        'filename' : value.filename,
                        'data' : base64.encodestring(tmp.read()),
                }
                
               
        return value


    def setData(self, fielddata, metadata):
        """sets all important field data
        """
        # update with new values
        self.logger.info('Updating object values (UID %s)' %
                metadata['UID'])
        
        
        fields = self.object.schema.fields()
        if HAS_AT_SCHEMAEXTENDER and queryAdapter(self.object, ISchemaExtender):
            fields += ISchemaExtender(self.object).getFields()
        
        for field in fields:
            fieldname = field.getName()
            # do not update "id" field
            if fieldname in fielddata.keys() and fieldname not in ['id']:
                field_value = fielddata[fieldname]
                #check for mode
                if field.mode != 'r':
                    field.getMutator(self.object)(field_value)
