from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class ZCMLLayer(ComponentRegistryLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        import ftw.publisher.core
        self.load_zcml_file('tests.zcml', ftw.publisher.core.tests)
        self.load_zcml_file('configure.zcml', ftw.publisher.core)


ZCML_LAYER = ZCMLLayer()


class PublisherCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.publisher.core
        xmlconfig.file('configure.zcml', ftw.publisher.core,
                       context=configurationContext)


PUBLISHER_CORE_FIXTURE = PublisherCoreLayer()
PUBLISHER_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PUBLISHER_CORE_FIXTURE,), name="PublisherCore:Integration")
