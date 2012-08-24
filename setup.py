from setuptools import find_packages
from setuptools import setup


setup(
    name='collective.cart.shopping',
    version='0.0',
    description="Make folderish plone object shopping site.",
    long_description='',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/collective.cart.shopping/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.cart'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.behavior.discount',
        'collective.behavior.size',
        'collective.behavior.stock',
        'collective.behavior.vat',
        'collective.cart.core',
        'collective.cart.shipping',
        'five.grok',
        'hexagonit.testing',
        'plone.app.imaging',
        'plone.app.textfield',
        'plone.directives.form',
        'plone.browserlayer',
        'plone.namedfile [blobs]',
        'setuptools',
        'zope.i18nmessageid'],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
