Overview
----------------------

Graphite-dashgen automates the creation of host dashboards based on existing
collectd_ metrics. Unlike the alternatives below,
this project seeks to use existing Graphite_ 0.9.9+ code.

.. _collectd: http://www.collectd.org/
.. _Graphite: http://graphite.wikidot.com/

Alternatives
----------------------

Note that these projects existed before Graphite included a dashboard view.

- `Etsy Dashboards <https://github.com/etsy/dashboard>`_
- `GDash <https://github.com/ripienaar/gdash>`_
- `Graphiti <https://github.com/paperlesspost/graphiti>`_
- `Tattle <https://github.com/wayfair/Graphite-Tattle>`_

Assumptions
----------------------

At least initially, Graphite-dashgen will cater to the following assumptions:

1. Data collected with collectd_
2. Sent to carbon with collectd-carbon_
3. Stored and displayed in Graphite_ 0.9.9+

.. _collectd-carbon: https://github.com/indygreg/collectd-carbon

Crontab Example
----------------------

::

    # Graphite Maintenance
    # Delete stale Graphite data
    @daily find /opt/graphite/storage/whisper/collectd/ -type f -mtime +90 -ls -delete
    # Delete empty directories
    @daily find /opt/graphite/storage/whisper/collectd/ -type d -empty -ls -delete
    # Regenerate all dashboards
    @daily /usr/local/sbin/dashgen.py -q -c /usr/local/etc/dashgen/ all '*'

Graph Definition Notes
----------------------

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

To Do
----------------------

- More documentation!
- Use templates with different colorList to easily differentiate graphs
- use dash profile options before defaults
- (?) should graphs be sorted by parent instead of children (ex. all disk
  ``vda`` graphs before any ``vdb`` graphs)

Contributors
----------------------

- https://github.com/TimBaldoni
- https://github.com/insyte

License
----------------------

Graphite-dashgen is licensed under the `BSD 2-Clause License
<http://www.opensource.org/licenses/BSD-2-Clause>`_

    Copyright (c) 2011, Clockwork Active Media Systems
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    - Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
