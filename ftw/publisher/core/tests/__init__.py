from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
import unittest


class IntegrationTestCase(unittest.TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))

    def set_workflow(self, mapping=None, **kwargs):
        mapping = mapping or {}
        mapping.update(kwargs)
        portal_workflow = getToolByName(self.portal, 'portal_workflow')
        portal_types = getToolByName(self.portal, 'portal_types')
        for portal_type, workflow in mapping.items():
            self.assertIn(portal_type, portal_types.objectIds(), 'Unknown portal_type.')
            self.assertIn(workflow, portal_workflow.objectIds() + [None], 'Unknown workflow.')
            portal_workflow.setChainForPortalTypes([portal_type], workflow)
