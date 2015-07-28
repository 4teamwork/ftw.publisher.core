from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core.testing import PUBLISHER_CORE_INTEGRATION_TESTING
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.component import getAdapter
import json


class TestSimplelayoutPageAnnotations(TestCase):
    layer = PUBLISHER_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_data_getter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))

        IPageConfiguration(page).store(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            })

        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutPageAnnotations')
        self.assertEquals(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            },
            json.loads(json.dumps(component.getData())))

    def test_data_setter(self):
        page = create(Builder('sl content page').titled(u'The Page'))
        block = create(Builder('sl textblock').titled(u'The Block').within(page))
        component = getAdapter(page, IDataCollector,
                               name='ftw.simplelayout:SimplelayoutPageAnnotations')
        component.setData(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            }, {})

        self.assertEquals(
            {
                "default": [
                    {"cols": [
                        {"blocks": [
                            {"uid": IUUID(block)}
                        ]},
                    ]},
                ]
            }, IPageConfiguration(page).load())
