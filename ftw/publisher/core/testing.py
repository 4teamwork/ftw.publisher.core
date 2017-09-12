from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder.testing import BUILDER_LAYER
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.portlets import portlets
from plone.app.portlets.portlets import navigation
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.content import Container
from plone.portlet.collection import collection
from plone.portlet.static import static
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.supermodel import model
from plone.testing import z2
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
import ftw.contentpage.tests.builders
import ftw.publisher.core.tests.builders
import ftw.shop.tests.builders
import ftw.simplelayout.tests.builders
import pkg_resources


try:
    pkg_resources.get_distribution('plonetheme.onegov')
except pkg_resources.DistributionNotFound:
    ONEGOV_THEME_INSTALLED = False
else:
    ONEGOV_THEME_INSTALLED = True


class IDummyIface(Interface):
    """This is a dummy interface"""


class IDummyIface2(Interface):
    """This is a dummy interface"""


class IDummyIface3(Interface):
    """This is a dummy interface"""

class ISampleContentSchema(model.Schema):
    pass


class ISampleContententMarker(Interface):
    pass


class SampleContent(Container):
    implements(ISampleContententMarker)


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

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.publisher.core.tests" file="behaviors.zcml" />'
            '</configure>',
            context=configurationContext)

        if ONEGOV_THEME_INSTALLED:
            # Load ZCML
            import plonetheme.onegov
            xmlconfig.file('configure.zcml', plonetheme.onegov,
                           context=configurationContext)

        z2.installProduct(app, 'ftw.contentpage')
        z2.installProduct(app, 'ftw.shop')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.relationfield:default')
        applyProfile(portal, 'ftw.simplelayout.contenttypes:default')
        applyProfile(portal, 'ftw.contentpage:default')
        applyProfile(portal, 'ftw.shop:default')
        applyProfile(portal, 'collective.z3cform.datagridfield:default')


PUBLISHER_CORE_FIXTURE = PublisherCoreLayer()
PUBLISHER_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PUBLISHER_CORE_FIXTURE,), name="PublisherCore:Integration")


class PublisherExampleContentLayer(PloneSandboxLayer):

    defaultBases = (PUBLISHER_CORE_INTEGRATION_TESTING,)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        self.folder = portal.get(portal.invokeFactory(
                'Folder', 'testing_example_data'))

        # add some default plone types
        testdoc1id = self.folder.invokeFactory('Document', 'test-doc-1')
        self['testdoc1'] = getattr(self.folder, testdoc1id, None)
        folder1id = self.folder.invokeFactory('Folder', 'test-folder-1')
        self['folder1'] = getattr(self.folder, folder1id, None)
        folderid2 = self.folder.invokeFactory('Folder', 'test-folder-2')
        self['folder2'] = getattr(self.folder, folderid2, None)
        testdoc2id = self['folder1'].invokeFactory('Document', 'test-doc-2')
        self['testdoc2'] = getattr(self['folder1'], testdoc2id, None)
        # create a topic
        topicid = self.folder.manage_addProduct['ATContentTypes'].addATTopic(
            id='atopic', title='A topic')
        self.topic = getattr(self.folder, topicid, None)

        # set some custom properties
        self['testdoc1'].manage_addProperty(id='bool', value=True,
                                         type='boolean')
        self['testdoc1'].manage_addProperty(id='date', value='2000/01/01',
                                         type='date')
        self['testdoc1'].manage_addProperty(id='float', value=2.1,
                                         type='float')
        self['testdoc1'].manage_addProperty(id='int', value=2,
                                            type='int')
        self['testdoc1'].manage_addProperty(id='lines',
                                         value=('row1', 'row2'),
                                         type='lines')
        self['testdoc1'].manage_addProperty(id='string',
                                         value='Hello World!',
                                         type='string')

        # put some custom portlets on folder1 - prepare to get
        # portlets from folder 2
        self['left_column'] = getUtility(IPortletManager,
                                      name=u'plone.leftcolumn',
                                      context=self['folder1'])

        self['left_column2'] = getUtility(IPortletManager,
                                       name=u'plone.leftcolumn',
                                       context=self['folder2'])

        self['right_column'] = getUtility(IPortletManager,
                                       name=u'plone.rightcolumn',
                                       context=self['folder1'])
        self['right_column2'] = getUtility(IPortletManager,
                                        name=u'plone.rightcolumn',
                                        context=self['folder2'])
        self['left_portlets'] = getMultiAdapter(
            (self['folder1'], self['left_column'],),
            IPortletAssignmentMapping, context=self['folder1'])

        self['left_portlets2'] = getMultiAdapter(
            (self['folder1'], self['left_column'],),
            IPortletAssignmentMapping, context=self['folder2'])
        self['right_portlets'] = getMultiAdapter(
            (self['folder1'], self['right_column'],),
            IPortletAssignmentMapping, context=self['folder1'])
        self['right_portlets2'] = getMultiAdapter(
            (self['folder1'], self['right_column'],),
            IPortletAssignmentMapping, context=self['folder2'])

        # static-text-portlets on right and left column
        self['left_portlets']['title1'] = static.Assignment(
            header='Title1', text="some text", omit_border=False)
        self['right_portlets']['title2'] = static.Assignment(
            header='Title2', text="some text", omit_border=False)
        self['right_portlets']['blubb'] = static.Assignment(
            header='blubb', text="some text", omit_border=False)
        self['right_portlets']['news'] = portlets.news.Assignment()
        self['right_portlets']['search'] = portlets.search.Assignment()
        # collection portlet on the right
        self['right_portlets']['collection'] = collection.Assignment(
            header="My collection",
            target_collection='/'.join(self.topic.getPhysicalPath()),
            limit="5",
            random=False,
            show_more=False,
            show_dates=True,
            )

        # custom Navigation portlet on the left side
        self['left_portlets']['custom_navigation'] = navigation.Assignment(
            name="custom Navigation",
            root='/'.join(self.folder.getPhysicalPath()),
            )

        # set dummy interfaces
        alsoProvides(self['testdoc1'], IDummyIface)
        alsoProvides(self['testdoc1'], IDummyIface2)
        alsoProvides(self['folder2'], IDummyIface2)
        alsoProvides(self['folder2'], IDummyIface3)

    def tearDownPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        aq_parent(aq_inner(self.folder)).manage_delObjects(
            [self.folder.id])


PUBLISHER_EXAMPLE_CONTENT_FIXTURE = PublisherExampleContentLayer()
PUBLISHER_EXAMPLE_CONTENT_INTEGRATION = IntegrationTesting(
    bases=(PUBLISHER_EXAMPLE_CONTENT_FIXTURE,),
    name="PublisherExampleContent:Integration")
