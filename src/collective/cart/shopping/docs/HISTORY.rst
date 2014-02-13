Changelog
---------

0.9 (2014-02-13)
================

- Add validation for SKU. [taito]

0.8.1 (2013-11-13)
==================

- Remove cache articles and article containers to list on vielwets since it does not work in some circumstances. [taito]

0.8 (2013-11-12)
================

- Add field image to content type: collective.cart.shopping.ArticleContainer. [taito]
- Add viewlet to article containers within it. [taito]
- Cache articles and article containers to list on vielwets. [taito]

0.7 (2013-11-06)
================

- Fix module name template.py -> view.py [taito]

0.6 (2013-10-30)
================

- Add javascript to update maxlength and size when selecting subarticle. [taito]
- Add street address to order listing. [taito]
- Added permission to show stock at add to cart form. [taito]
- Fixed method: is_check_out_view for case where last pass is not view. [taito]
- Moved check out buttons javascript from template to its own file. [taito]
- Fixed translations and styles. [taito]
- Added order listing views. [taito]
- Removed dependency from five.grok. [taito]
- Updated translation. [taito]
- Moved test package to extras_require. [taito]
- Added SCRF authenticator. [taito]
- Removed subscriber: update_path_for_intId which was temporary. [taito]

0.5 (2013-03-26)
================

- Hidden shipping cost when it is free. [taito]
- Localized money and vat rate. [taito]

0.4 (2013-03-18)
================

- Added method: link_to_order_for_customer to adapter ShippingMethod. [taito]

0.3 (2013-03-16)
================

- Updated for session cart. [taito]
- Added article listing with export button to csv.[taito]
- Removed content type: SubArticle. [taito]
- Added stock view for articles. [taito]
- Fixed subscriber to enable pasting articles. [taito]
- Added viewlet to show related articles. [taito]
- Added event signaling "add to cart" and its subscriber to show status message about it. [taito]
- Added case when shipping method does not exsits. [taito]
- Added subscriber to send e-mail when ordered. [taito]
- Added "Back" button to check out process. [taito]
- Added thanks page. [taito]
- Added testing integration to Travis CI. [taito]
- Covered tests. [taito]
- And lots more... [taito]

0.2.1 (2012-09-25)
==================

- Updated for translations. [taito]

0.2 (2012-09-24)
================

- Added content type: Article Container. [taito]

0.1.1 (2012-09-20)
==================

- Added collective.cart.shopping.CustomerInfo and collective.cart.stock.Stock to types_not_searched and metaTypesNotToList properties. [taito]

0.1 (2012-09-19)
================

- Initial release. [taito]
