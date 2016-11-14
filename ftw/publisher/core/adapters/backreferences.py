from AccessControl.SecurityInfo import ClassSecurityInformation
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import SpecialUsers
from Acquisition import aq_base
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.CMFCore.utils import getToolByName
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.interface import implements


class Backreferences(object):
    """ Resets backreferences (pointing from another already released
    object to "me").
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, obj):
        self.context = obj

    security.declarePrivate('getData')
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

        if hasattr(aq_base(self.context), 'getBackReferenceImpl'):
            referenceable = self.context

        else:
            try:
                referenceable = IReferenceable(self.context)

            except TypeError:
                # could not adapt
                # this means we have a dexterity object without
                # plone.app.referenceablebehavior activated.
                return data

        old_security_manager = getSecurityManager()
        newSecurityManager(self.context.REQUEST, SpecialUsers.system)
        try:
            references = referenceable.getBackReferenceImpl()
        finally:
            setSecurityManager(old_security_manager)

        for ref in references:
            # get source object
            src = ref.getSourceObject()
            if src is None:
                continue

            suid = src.UID()

            if suid not in data.keys():
                data[suid] = {}
            if getattr(ref, 'field', None) is None:
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

    security.declarePrivate('setData')
    def setData(self, data, metadata):
        self.logger.info('Updating backreferences (UID %s)' %
                         metadata['UID'])
        cuid = self.context.UID()
        reference_catalog = getToolByName(self.context, 'reference_catalog')

        for suid, mapping in data.items():
            sobj = reference_catalog.lookupObject(suid)
            if not sobj:
                # source object is not published
                continue

            self.logger.info('... source-obj: %s' % '/'.join(
                    sobj.getPhysicalPath()))
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
                        tobj = reference_catalog.lookupObject(tuid)
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
