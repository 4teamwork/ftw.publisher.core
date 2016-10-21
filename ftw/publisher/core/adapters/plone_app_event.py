from AccessControl.SecurityInfo import ClassSecurityInformation
from plone.app.event.dx.behaviors import data_postprocessing


class FixEventTimezones(object):
    """
    plone.app.event's IEventBasic stores temporarily FakeZone objects
    as tzinfo of start and end dates.
    This is cleaned up by data_postprocessing when the modification event is fired.
    But the publisher does not fire the modification event.
    Because we do not want to have side effects by introducing firing the modification
    event we trigger the post processing manually.

    The data collector adapters are executed in order of their names.
    This adapter should be executed after the dx_field_data_adapter, so we prefix
    the name of the adapter with zzz_.
    """
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    def getData(self):
        return None

    def setData(self, data, metadata):
        data_postprocessing(self.context, None)
