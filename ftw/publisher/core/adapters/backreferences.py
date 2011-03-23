from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.interface import implements


class Backreferences(object):
    """ Resets backreferences (pointing from another already released
    object to "me").
    """

    implements(IDataCollector)
    logger = getLogger()

    def __init__(self, obj):
        self.context = obj

    def getData(self):
        """ Returns backreferences:
        {
            'uid-obj-a': {
                'the-field': [
                    'uid-of-another-unpublished-object',
                    'my-uid',
                    'uid-obj-b',
                ],
            },
            'uid-obj-b': {
                'ref-field': 'my-uid',
            },
        }
        """

        data = {}
        for ref in self.context.getBackReferenceImpl():
            # get source object
            src = ref.getSourceObject()
            suid = src.UID()

            if suid not in data.keys():
                data[suid] = {}
            if getattr(ref, 'field', None) == None:
                continue

            if ref.field in data[suid]:
                # we already added this field
                continue
            else:
                # add the field value
                field = src.getField(ref.field)
                if field:
                    data[suid][ref.field] = field.getRaw(src)

        return data

    def setData(self, data, metadata):
        self.logger.info('Updating backreferences (UID %s)' %
                         metadata['UID'])
        cuid = self.context.UID()
        atool = self.context.archetype_tool

        for suid, mapping in data.items():
            sobj = atool.getObject(suid)
            if not sobj:
                # source object is not published
                continue

            self.logger.info('... source-obj: %s' % '/'.join(sobj.getPhysicalPath()))
            for fieldname, value in mapping.items():
                # value maybe uid (str) or list of uids (list)
                if isinstance(value, str):
                    value = [value]
                    single = True
                else:
                    single = False
                new_value = []

                # only set the targets that exist (=may be published)
                for tuid in value:
                    if tuid == cuid:
                        new_value.append(self.context)
                    else:
                        tobj = atool.getObject(tuid)
                        if tuid:
                            new_value.append(tobj)

                # set the new value on the field
                field = sobj.getField(fieldname)
                if single and new_value:
                    field.set(sobj, new_value[0])
                elif single:
                    field.set(sobj, None)
                else:
                    field.set(sobj, new_value)
