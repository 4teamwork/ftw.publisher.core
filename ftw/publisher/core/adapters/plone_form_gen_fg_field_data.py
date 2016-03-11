from ftw.publisher.core.interfaces import IDataCollector
from zope.interface import implements


class PloneFormGenFGFieldDataCollector(object):
    """DataCollector adapter for ploneformgen fgfield.

    Some field types, i.e. the FGRichLabelField has stored the
    field 'fgField' as an instance attribute instead in the schema.

    This DataCollector collects the 'fgField' from PloneFormGen fields.
    """
    implements(IDataCollector)
    field_name = 'fgField'

    def __init__(self, context):
        self.context = context

    def getData(self):
        data = {}

        if not hasattr(self.context, self.field_name):
            return data

        field = getattr(self.context, self.field_name)

        # We have to get the 'default'-value. The getRaw method will not
        # return the correct value.
        data[self.field_name] = field.getDefault(self.context)

        return data

    def setData(self, data, metadata):
        value = data.get(self.field_name, None)
        if not value:
            return data

        field = getattr(self.context, self.field_name)

        # We have to set the 'default'-value because setting the value
        # through the set mehtod will not set the correct value.
        field.default = value
