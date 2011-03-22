from setuptools import setup, find_packages
import os

version = open('ftw/publisher/core/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require=[
    'collective.testcaselayer',
    ]

setup(name='ftw.publisher.core',
      version=version,
      description="Core package of Product publisher" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ftw publisher core',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/4teamwork/ftw/ftw.publisher.core/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.publisher'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
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
