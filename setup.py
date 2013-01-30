from setuptools import setup, find_packages
import os

version = '2.0.dev0'
maintainer = 'Jonas Baumann'

tests_require=[
    'collective.testcaselayer',
    'Plone',
    'plone.app.testing',
    'plone.app.blob',
    'ftw.testing',
    ]

setup(name='ftw.publisher.core',
      version=version,
      description="Staging and publishing addon for Plone contents.",
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw publisher core',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.publisher.core',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.publisher'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'ZConfig',
        ],

      extras_require={
        'tests': tests_require,
        },

      tests_require=tests_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
