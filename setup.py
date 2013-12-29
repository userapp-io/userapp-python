from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='userapp',
      version=version,
      description="Client for accessing the UserApp API.",
      long_description="""\
Client library for making calls to the UserApp API.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='user management api authentication oauth',
      author='Robin Orheden',
      author_email='robin.orheden@userapp.io',
      url='https://www.userapp.io/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
