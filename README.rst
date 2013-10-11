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
    0   22  *   *   *   find /opt/graphite/storage/log/ -type f -mtime +180 -delete
    0   22  *   *   *   find /opt/graphite/storage/whisper/collectd/ -type f -mtime +90 -delete
    0   22  *   *   *   find /opt/graphite/storage/whisper/statsd/ -type f -mtime +90 -delete
    # Delete empty directories
    0   23  *   *   *   find /opt/graphite/storage/log/ -type d -empty -delete
    0   23  *   *   *   find /opt/graphite/storage/whisper/collectd/ -type d -empty -delete
    0   23  *   *   *   find /opt/graphite/storage/whisper/statsd/ -type d -empty -delete
    # Regenerate all dashboards
    @daily /usr/local/sbin/dashgen.py -q -f /usr/local/etc/dashgen/dashconf.yml -f /usr/local/etc/dashgen/all_*.yml -H '*'

Graph Definition Notes
======================

- Target entries are as close to web GUI as possible to make it easier to go
  back and forth

- Dashboard Types

  1. Per-Host
  2. Per-Group

- Per-Host Graph Types

  1. Host Metrics: identified by ``glob_verify`` and may contain
     ``glob_metrics``
  2. Carbon Metrics: identified by ``carbon_match`` and host

- String Templates: named substitutions draw from ``target_vars``. Graph
  definitions that contain named substitutions not in `target_vars` are
  skipped. Common `target_vars` include:

  - ``${color_combined}``
  - ``${color_free}``
  - ``${host}``
  - ``${metric}``

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
