from AccessControl.SecurityInfo import ClassSecurityInformation
from DateTime import DateTime
from plone.app.event.dx.interfaces import IDXEvent


class FixEventTimezones(object):
    """
    Because plone.app.event's IEventBasic has a separate timezone field,
    it does some strange things with FakeZone on start / end.
    This leads to problems when publishing with the regulare publisher
    field adapter.

    In order to fix to those issues we handle start / end dates in this
    adapter explicitly, so that we have full control.
    """
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    def getData(self):
        event = IDXEvent(self.context)
        return {'start': DateTime(event.start),
                'end': DateTime(event.end)}

    def setData(self, data, metadata):
        event = IDXEvent(self.context)
        event.start = data['start'].asdatetime()
        event.end = data['end'].asdatetime()
