# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.collectionwidget package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() +
    '\nContributors\n============\n\n' +
    open('CONTRIBUTORS.rst').read() + '\n\n' +
    open('CHANGES.rst').read() + '\n')

setup(
    name='collective.eeafaceted.collectionwidget',
    version='1.5',
    description=(
        "eea.facetednavigation widget that enables selecting "
        "a collection (among several) as base filter"),
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone faceted navigation widget collection',
    author='IMIO',
    author_email='support@imio.be',
    url='http://pypi.python.org/pypi/collective.eeafaceted.collectionwidget',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.eeafaceted'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'collective.behavior.talcondition',
        'eea.facetednavigation >= 10.0',
        'imio.helpers',
        'plone.app.contenttypes',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
