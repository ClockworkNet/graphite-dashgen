#!/usr/bin/python

from datetime import date
import glob
import json
import logging
import logging.handlers
from optparse import OptionParser
import os
import sys
import urllib
import yaml

"""USAGE: %prog [options] PROFILE HOST [HOST...]
"""

log = logging.getLogger('dashgen')
screenhdlr = logging.StreamHandler()
screenfmt = logging.Formatter('%(levelname)s %(message)s')
screenhdlr.setFormatter(screenfmt)
# Allows this code to be reloaded interactively without ending up with
# multiple log handlers
log.handlers = list()
log.addHandler(screenhdlr)


def dash_create(host, host_path, profile):
    """Create dashboard for specified host and dashboard profile
    """
    defaults = dashconf['defaults']
    today = date.today().strftime('%FT%T')
    dash_name = "%s_%s" % (host, profile)
    log.info("Dashboard: %s" % dash_name)

    # dashboard
    dash = {
            'name': dash_name,
            'defaultGraphParams': {
                'width': defaults['width'],
                'height': defaults['height'],
                'from': '-%s%s' % (defaults['quantity'], defaults['units']),
                'until': defaults['until'],
                'fontName': defaults['fontName'],
                },
            'refreshConfig': {
                'interval': defaults['interval'],
                'enabled': defaults['enabled'],
                },
            'graphs': list(),
            'timeConfig': {
                'startDate': today,
                'endDate': today,
                'startTime': defaults['startTime'],
                'endTime': defaults['endTime'],
                'quantity': defaults['quantity'],
                'type': defaults['type'],
                'units': defaults['units'],
#
# seems that the new time handling is less than complete
#
#                'relativeStartUnits': defaults['relativeStartUnits'],
#                'relativeStartQuantity': defaults['relativeStartQuantity'],
#                'relativeUntilUnits': defaults['relativeUntilUnits'],
#                'relativeUntilQuantity': defaults['relativeUntilQuantity'],
                },
            'graphSize': {
                'width': defaults['width'],
                'height': defaults['height'],
                },
            }
    dash['graphs'] = graph_create(host, host_path)
    return dash


def graph_create(host, host_path):
    """Create graph for specified host and dashboard profile
    """
    graphs = list()
    for name in dash_profile['graphs']:
        log.info("  Graph: %s" % name)
        graph = list()
        # Skip undefined graphs
        if name not in graphdef.keys():
            log.error("%s not found in graphdef.yml" % name)
            continue
        # Graph Type #1: Host Metrics
        #   Identified by filesytem globbing
        elif 'glob_verify' in graphdef[name].keys():
            # Determine and test metric paths
            if 'glob_metrics' in graphdef[name].keys():
                glob_metrics = graphdef[name]['glob_metrics']
                metric_verify = True
            else:
                glob_metrics = graphdef[name]['glob_verify']
                metric_verify = False
            metric_glob = "%s/%s" % (host_path, glob_metrics)
            metric_paths = glob.glob(metric_glob)
            if len(metric_paths) <= 0:
                continue
            metric_paths.sort()
            for metric_path in metric_paths:
                graph_object = dict(graphdef[name])
                # Verify metric path
                if metric_verify:
                    verify_glob = "%s/%s" % (metric_path,
                            graphdef[name]['glob_verify'])
                    del(graph_object['glob_metrics'])
                else:
                    verify_glob = metric_path
                if len(glob.glob(verify_glob)) != 1:
                    continue
                del(graph_object['glob_verify'])
                metric = os.path.basename(metric_path)
                log.debug("    metric: %s" % metric)
                graph = graph_compile(host, name, graph_object, metric)
                if len(graph) > 0:
                    graphs.append(graph)
        # Graph Type #2: Carbon Match
        #   Metrics reported directly by carbon server to itself
        elif ('carbon_match' in graphdef[name].keys() and
                graphdef[name]['carbon_match'] and
                host == dashconf['carbon_match']):
            graph_object = dict(graphdef[name])
            del graph_object['carbon_match']
            graph = graph_compile(
                    dashconf['carbon_server'], name, graph_object, None)
            if len(graph) > 0:
                graphs.append(graph)
    return graphs


def graph_compile(host, name, graph_object, metric):
    """Finish compiling graph
    """
    # Graphs consist of 3 parts
    #   1. graph_targets
    #   2. graph_object
    #   3. graph_render
    color_combined = dashconf['color_combined']
    color_free = dashconf['color_free']
    # target
    templates = graph_object.pop('target')
    target_object = list()
    target_pairs = list()
    for template in templates:
        target = template % {
                'color_combined': color_combined,
                'color_free': color_free,
                'host': host,
                'metric': metric,
                }
        target_object.append(target)
        target_pairs.append(('target', target))
    graph_targets = urllib.urlencode(target_pairs)
    # title
    if 'title' in graph_object.keys():
        graph_object['title'] = graph_object['title'] % {
                'metric': metric
                }
    else:
        graph_object['title'] = name
    graph_object['title'] = graph_object['title'].replace('-', '.')
    # build graph_render
    graph_render = "/render?%s&%s" % (
            urllib.urlencode(graph_object),
            graph_targets
            )
    # add target(s) to graph_object
    graph_object['target'] = target_object
    return [graph_targets, graph_object, graph_render]


def dash_save(dash):
    """Save dashboard using Graphite libraries
    """
    # Graphite libraries
    sys.path.append(dashconf['webapp_path'])
    os.environ['DJANGO_SETTINGS_MODULE'] = "graphite.settings"
    from graphite.dashboard.models import Dashboard

    dash_name = dash['name']
    dash_state = str(json.dumps(dash))
    try:
        dashboard = Dashboard.objects.get(name=dash_name)
    except Dashboard.DoesNotExist:
        dashboard = Dashboard.objects.create(name=dash_name, state=dash_state)
    else:
        dashboard.state = dash_state
        dashboard.save()


def set_log_level(opts):
    global log
    """Set the logging level."""
    loglevel = opts.verbose - opts.quiet
    if loglevel >= 2:
        log.setLevel(logging.DEBUG)
    elif loglevel == 1:
        log.setLevel(logging.INFO)
    elif loglevel == 0:
        log.setLevel(logging.WARN)
    elif loglevel < 0:
        log.setLevel(logging.CRITICAL)


def parser_setup():
    """Instantiate, configure, and return an OptionParser instance.
    """
    p = OptionParser(__doc__)
    p.add_option("-c", "--config-dir", default='.',
            help="Configuration directory. Contains YAML configuration files.")
    p.add_option("-v", "--verbose", action="count", default=1,
            help="Print copious debugging info.")
    p.add_option("-q", "--quiet", action="count", default=0,
            help="Suppress output. -qq to suppress ALL output.")
    return p


def main():
    global dashconf, dash_profile, graphdef
    # Command Line Options
    p = parser_setup()
    opts, args = p.parse_args()
    set_log_level(opts)
    try:
        profile = args.pop(0)
    except:
        log.error("PROFILE must be specified")

    # read yaml configuration files
    dashconf = yaml.load(open('%s/dashconf.yml' % opts.config_dir, 'r'))
    dashdef = yaml.load(open('%s/dashdef.yml' % opts.config_dir, 'r'))
    graphdef = yaml.load(open('%s/graphdef.yml' % opts.config_dir, 'r'))
    try:
        dash_profile = dashdef.pop(profile)
    except:
        log.error("Invalid dashboard profile specified: '%s'" % profile)

    # Build hosts list
    host_parent_glob = "%s/%s" % (
            dashconf['whisper_path'], dashconf['source_glob'])
    host_paths = list()
    for arg in args:
        for host_path in glob.iglob("%s/%s" % (host_parent_glob, arg)):
            host_path = os.path.abspath(host_path)
            if os.path.isdir(host_path):
                host_paths.append(host_path)
    host_paths.sort()

    for host_path in host_paths:
        host = os.path.basename(host_path)
        dash = dash_create(host, host_path, profile)
        dash_save(dash)


if __name__ == "__main__":
    main()
