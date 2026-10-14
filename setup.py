"""Installer for the collective.eeafaceted.collectionwidget package."""

from setuptools import find_packages
from setuptools import setup

long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"

setup(
    name="collective.eeafaceted.collectionwidget",
    version="2.0.0.dev0",
    description=(
        "eea.facetednavigation widget that enables selecting "
        "a collection (among several) as base filter"
    ),
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="Plone faceted navigation widget collection",
    author="IMIO",
    author_email="support@imio.be",
    url="http://pypi.python.org/pypi/collective.eeafaceted.collectionwidget",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective", "collective.eeafaceted"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "collective.behavior.talcondition",
        "eea.facetednavigation >= 16.0",
        "imio.helpers",
        "plone.api",
        "plone.app.contentlisting",
        "plone.app.contenttypes",
        "plone.app.querystring",
        "plone.autoform",
        "plone.base",
        "plone.indexer",
        "plone.memoize",
        "Products.CMFCore",
        "Products.ZCatalog",
        "z3c.form",
        "Zope",
    ],
    extras_require={
        "test": [
            "lxml",
            "plone.app.robotframework [debug]",
            "plone.app.testing",
            "plone.behavior",
            "plone.browserlayer",
            "plone.dexterity",
            "plone.testing",
            "robotsuite",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
