from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(
    name='ckanext-dsaudit',
    version=version,
    description="Activities for Auditing Datastore Changes",
    long_description="""
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Government of Canada',
    author_email='ian@excess.org',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points=\
    """
    [ckan.plugins]
    dsaudit=ckanext.dsaudit.plugins:DSAuditPlugin

    [babel.extractors]
    ckan=ckan.lib.extract:extract_ckan
    """,
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    },
)
