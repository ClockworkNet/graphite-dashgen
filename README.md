# Overview #

Graphite-dashgen will automate the creation of host dashboards based on existing
[collectd](http://www.collectd.org/) metrics. Unlike the alternatives below,
this project seeks to use existing [Graphite](http://graphite.wikidot.com/) 0.9.9+ code.

Also see [graphite_dashboards.sh](https://gist.github.com/1368022) for a naive
stop-gap solution.

# Alternatives #

Note that these projects existed before Graphite included a dashboard view.

- [GDash](https://github.com/ripienaar/gdash)
- [Etsy Dashboards](https://github.com/etsy/dashboard/)
- [Tattle](https://github.com/wayfair/Graphite-Tattle)

# Assumptions #

At least initially, Graphite-dashgen will cater to the followign assumptions:

1. Data collected with [collectd](http://www.collectd.org/)
1. Sent to carbon with [collectd-carbon](https://github.com/indygreg/collectd-carbon)
1. Stored and displayed in [Graphite](http://graphite.wikidot.com/) 0.9.9+
