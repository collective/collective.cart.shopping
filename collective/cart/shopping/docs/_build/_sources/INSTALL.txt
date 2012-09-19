Installation
------------

You may list ``collective.cart.stock`` to ``buildout.cfg`` or ``setup.py`` in your own package.

zc.buildout and the plone.recipe.zope2instance
==============================================

Use zc.buildout and the plone.recipe.zope2instance
recipe by adding ``collective.cart.stock`` to the list of egg::

    [buildout]
    ...
    eggs =
        ...
        collective.cart.stock


Dependency to your own package
==============================

You may also list to install_requires to ``setup.py`` within your package.
