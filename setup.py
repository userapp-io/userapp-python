from setuptools import setup, find_packages
import sys, os

version = '0.2.4'

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 2",
]

setup(name='userapp',
      version=version,
      description="Client for accessing the UserApp API.",
      long_description="""\
Client library for making calls to the UserApp API.""",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        ].extend(classifiers),
      keywords=["userapp", "user management", "api", "user authentication", "oauth"],
      author='Robin Orheden',
      author_email='robin.orheden@userapp.io',
      url='https://github.com/userapp-io/userapp-python/',
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
