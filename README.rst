Overview
=========

Graphite-dashgen automates the creation of host dashboards based on existing
collectd_ metrics. Unlike most of the alternatives below, this project seeks to
use existing Graphite_ 0.9.9+ code. It also allows the creation of grouped
boards.

.. _collectd: http://www.collectd.org/
.. _Graphite: http://graphite.wikidot.com/


Crontab Example
===============

::

    # Graphite Maintenance
    # Delete stale Graphite data
    @daily find /opt/graphite/storage/whisper/collectd/ -type f -mtime +90 -ls -delete
    # Delete empty directories
    @daily find /opt/graphite/storage/whisper/collectd/ -type d -empty -ls -delete
    # Regenerate all dashboards
    @daily /usr/local/sbin/dashgen.py -q -c /usr/local/etc/dashgen/ all '*'


Graph Definition Notes
======================

- Target entries are as close to web GUI as possible to make it easier to go
  back and forth

- Graph Types

  1. Host Metrics: identified by ``glob_verify`` and may contain
     ``glob_metrics``
  2. Carbon Metrics: identified by ``carbon_match`` and host

- Available String Replacements:

  - ``%(color_combined)s``
  - ``%(color_free)s``
  - ``%(host)s``
  - ``%(metric)s``

    - Only available to Host Metric graphs

- The combination of ``glob_metrics`` and ``glob_verify`` should result in a
  single filesystem glob match

- Lines drawn by graphite obscure the lines drawn before them. Z order is
  important. Consequently, many of the graphs' metrics change color depending
  on their values.

- For graphs that feature a free metric (ex. memory), that free metric is
  always green (green should not be included in the template's ``lineColor``)


Requirements
=============

- Graphite 0.9.9+
- `PyYAML`_

.. _`PyYAML`: https://pypi.python.org/pypi/PyYAML/


To Do
=====

- More documentation!
- Use templates with different ``colorList`` to easily differentiate graphs
- use dash profile options before defaults
- (?) should graphs be sorted by parent instead of children (ex. all disk
  ``vda`` graphs before any ``vdb`` graphs)


Alternatives
============

A slightly different (and refreshing) take on Graphite dashboards:

- `Tasseo <https://github.com/obfuscurity/tasseo>`_

The following projects existed before Graphite included a dashboard view:

- `Etsy Dashboards <https://github.com/etsy/dashboard>`_
- `GDash <https://github.com/ripienaar/gdash>`_
- `Graphiti <https://github.com/paperlesspost/graphiti>`_
- `Tattle <https://github.com/wayfair/Graphite-Tattle>`_

The Graphite 0.9.12 documentation includes a good list of related software:

- `Tools That Work With Graphite
  <http://graphite.readthedocs.org/en/0.9.12/tools.html>`_


Contributors
============

- https://github.com/TimZehta
- https://github.com/insyte


License
=======

- LICENSE_ (`MIT License`_)

.. _LICENSE: LICENSE
.. _`MIT License`: http://www.opensource.org/licenses/MIT
