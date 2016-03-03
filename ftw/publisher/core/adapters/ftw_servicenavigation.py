from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.servicenavigation.form import ANNOTATION_KEY
from zope.annotation import IAnnotations


class ServiceNavigationDataCollector(object):
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        annotations = IAnnotations(self.context)
        return annotations.get(ANNOTATION_KEY, {})

    security.declarePrivate('setData')
    def setData(self, data, metadata=None):
        annotations = IAnnotations(self.context)
        annotations[ANNOTATION_KEY] = data
