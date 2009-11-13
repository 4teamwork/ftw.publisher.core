from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ftw.publisher.core',
      version=version,
      description="Core package of Product publisher",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ftw publisher core',
      author='Jonas Baumann',
      author_email='j.baumann@4teamwork.ch',
      url='https://svn.4teamwork.ch/repos/ftw/ftw.publisher.core/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
