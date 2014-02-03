from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plonetheme.onegov.interfaces import ICustomStyles
from unittest2 import TestCase
from zope.component import getAdapter


class TestCustomStyling(TestCase):

    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.custom = ICustomStyles(self.portal)
        self.input_ = {'css.body-background': 'red'}
        self.custom.set_styles(self.input_)

    def test_custom_style_getter(self):
        component = getAdapter(self.portal, IDataCollector,
                               name='custom_style_adapter')

        data = component.getData()
        self.assertEquals(self.input_, data)

    def test_custom_style_setter(self):
        self.custom.set_styles({})
        component = getAdapter(self.portal, IDataCollector,
                               name='custom_style_adapter')
        self.assertEquals({}, component.getData())

        component.setData(self.input_, {})

        self.assertEquals(self.input_, component.getData())
