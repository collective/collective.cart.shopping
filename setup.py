from setuptools import find_packages
from setuptools import setup

import os


long_description = (
    open(os.path.join("src", "collective", "cart", "shopping", "docs", "README.rst")).read() + "\n" +
    open(os.path.join("src", "collective", "cart", "shopping", "docs", "HISTORY.rst")).read() + "\n" +
    open(os.path.join("src", "collective", "cart", "shopping", "docs", "CONTRIBUTORS.rst")).read())


setup(
    name='collective.cart.shopping',
    version='0.2.1.10',
    description="Shopping site suit for Plone.",
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/collective.cart.shopping/',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['collective', 'collective.cart'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFPlone',
        'collective.behavior.discount',
        'collective.behavior.size',
        'collective.behavior.sku',
        'collective.behavior.stock',
        'collective.behavior.vat',
        'collective.cart.core',
        'collective.cart.shipping',
        'five.grok',
        'five.pt',
        'hexagonit.testing',
        'plone.app.relationfield',
        'plone.app.textfield',
        'plone.directives.form',
        'plone.namedfile [blobs]',
        'setuptools'],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
