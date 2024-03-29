from setuptools import setup, find_packages
import os

version = '2.14.7.dev0'
maintainer = 'Jonas Baumann'

extras_require = {
    'dexterity': [
        'plone.app.dexterity',
        ],
    'tests_plone4': [
        'collective.geo.contentlocations',
        'collective.z3cform.datagridfield < 1.4.0',
        'ftw.shop',
        'plonetheme.onegov < 4.0.0'
    ]
}


extras_require['tests'] = tests_require = [
    'Acquisition',
    'Plone',
    'Products.PloneFormGen',
    'collective.z3cform.datagridfield',
    'ftw.builder',
    'ftw.servicenavigation',
    'ftw.simplelayout [contenttypes]',
    'ftw.testing',
    'plone.app.blob',
    'plone.app.contenttypes',
    'plone.app.relationfield',
    'plone.app.testing',
    'plone.directives.form',
    'plone.namedfile',
    'pytz',
    'zope.annotation',
    'zope.configuration',
] + extras_require['dexterity']


setup(name='ftw.publisher.core',
      version=version,
      description="Staging and publishing addon for Plone contents.",
      long_description=open("README.rst").read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw publisher core',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.publisher.core',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.publisher'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[

        'AccessControl',
        'Products.Archetypes',
        'Products.CMFCore',
        'ZConfig',
        'ZODB3',
        'Zope2',
        'plone.app.blob',
        'plone.portlets',
        'setuptools',
        'zope.component',
        'zope.dottedname',
        'zope.i18nmessageid',
        'zope.interface',

        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
