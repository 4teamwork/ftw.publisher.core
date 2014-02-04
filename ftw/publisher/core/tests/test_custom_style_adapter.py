from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import ONEGOV_THEME_INSTALLED
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.component import getAdapter
import unittest2



class TestCustomStyling(unittest2.TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        if ONEGOV_THEME_INSTALLED:
            from plonetheme.onegov.interfaces import ICustomStyles
            self.custom = ICustomStyles(self.portal)
            self.input_ = {'css.body-background': 'red'}
            self.custom.set_styles(self.input_)

    @unittest2.skipUnless(ONEGOV_THEME_INSTALLED,
                          'plonetheme.onegov not installed')
    def test_custom_style_getter(self):
        component = getAdapter(self.portal, IDataCollector,
                               name='custom_style_adapter')

        data = component.getData()
        self.assertEquals(self.input_, data)

    @unittest2.skipUnless(ONEGOV_THEME_INSTALLED,
                          'plonetheme.onegov not installed')
    def test_custom_style_setter(self):
        self.custom.set_styles({})
        component = getAdapter(self.portal, IDataCollector,
                               name='custom_style_adapter')
        self.assertEquals({}, component.getData())

        component.setData(self.input_, {})

        self.assertEquals(self.input_, component.getData())
