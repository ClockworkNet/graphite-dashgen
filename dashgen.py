#!/usr/bin/env python
"""Automates the creation of graphite dashboards based on either preexisting
metrics (per_host) or variables (per_group).
"""
# Standard library
import argparse
from datetime import date
import glob
from itertools import chain
import json
import logging
import logging.handlers
import os
import socket
import string
import sys
import urllib
# Third-party
import yaml

dashconf = {"defaults": dict()}
graphsconf = dict()

# Logging
log = logging.getLogger("dashgen")
screenhdlr = logging.StreamHandler()
screenfmt = logging.Formatter("%(levelname)s %(message)s")
screenhdlr.setFormatter(screenfmt)
# Allows this code to be reloaded interactively without ending up with
# multiple log handlers
log.handlers = list()
log.addHandler(screenhdlr)

# socket
try:
    socket.setdefaulttimeout(1)
except:
    pass


def dash_create(dash_name):
    """Create dashboard for specified host and dashboard profile."""
    defaults = dashconf["defaults"]
    today = date.today().strftime("%FT%T")
    log.info("Dashboard: %s" % dash_name)

    # dashboard
    dash = {"name": dash_name,
            "defaultGraphParams": {
                "width": defaults["width"],
                "height": defaults["height"],
                "from": "-%s%s" % (defaults["quantity"], defaults["units"]),
                "until": defaults["until"],
                "format": defaults["format"],
            },
            "refreshConfig": {
                "interval": defaults["interval"],
                "enabled": defaults["enabled"],
            },
            "graphs": list(),
            "timeConfig": {
                "startDate": today,
                "endDate": today,
                "startTime": defaults["startTime"],
                "endTime": defaults["endTime"],
                "quantity": defaults["quantity"],
                "type": defaults["type"],
                "units": defaults["units"],
                #
                # seems that the new time handling is less than complete
                #
                # "relativeStartUnits": defaults["relativeStartUnits"],
                # "relativeStartQuantity": defaults["relativeStartQuantity"],
                # "relativeUntilUnits": defaults["relativeUntilUnits"],
                # "relativeUntilQuantity": defaults["relativeUntilQuantity"],
            },
            "graphSize": {
                "width": defaults["width"],
                "height": defaults["height"],
            },
            }
    return dash


def resolve_name(graph, ip_str):
    if ("resolve_metric" not in graphsconf[graph] or
            not graphsconf[graph]["resolve_metric"]):
        return ip_str
    try:
        ip = ip_str.replace("-", ".")
        metric_resolved = socket.gethostbyaddr(ip)[0]
        return metric_resolved.replace(".", "_")
    except:
        return ip_str


def per_group_graph_create(group):
    """Create graph for specified host and dashboard profile."""
    graphs = list()
    for name in dashconf["include"]:
        log.info("  Graph: %s" % name)
        graph = list()
        # Skip undefined graphs
        if name not in graphsconf:
            log.error("%s not found in graphs configuration" % name)
            continue
        else:
            target_vars = dashconf["target_vars"]
            target_vars.update(dashconf["groups"][group])
            target_vars.update({"metric": name})
            graph_object = dict(graphsconf[name])
            graph = graph_compile(name, graph_object, target_vars)
            if graph:
                graphs.append(graph)
    return graphs


def per_host_graph_create(host, host_path):
    """Create graph for specified host and dashboard profile."""
    graphs = list()
    for name in dashconf["include"]:
        log.info("  Graph: %s" % name)
        # Skip undefined graphs
        if name not in graphsconf:
            log.error("%s not found in graphs configuration" % name)
            continue
        graph = list()
        target_vars = dashconf["target_vars"]
        # Graph Type #1: Host Metrics
        #   Identified by filesytem globbing
        if "glob_verify" in graphsconf[name]:
            # Determine and test metric paths
            if "glob_metrics" in graphsconf[name]:
                glob_metrics = graphsconf[name]["glob_metrics"]
                metric_verify = True
            else:
                glob_metrics = graphsconf[name]["glob_verify"]
                metric_verify = False
            metric_glob = "%s/%s" % (host_path, glob_metrics)
            metric_paths = glob.glob(metric_glob)
            if len(metric_paths) <= 0:
                log.debug("    (no metrics found)")
                continue
            metric_paths.sort()
            for metric_path in metric_paths:
                graph_object = dict(graphsconf[name])
                # Verify metric path
                if metric_verify:
                    verify_glob = "%s/%s" % (metric_path,
                                             graphsconf[name]["glob_verify"])
                    del(graph_object["glob_metrics"])
                else:
                    verify_glob = metric_path
                if len(glob.glob(verify_glob)) != 1:
                    continue
                del(graph_object["glob_verify"])
                metric = os.path.basename(metric_path)
                log.debug("    metric: %s" % metric)

                metric_resolved = resolve_name(name, metric)
                del graph_object["resolve_metric"]

                target_vars.update({"host": host, "metric": metric,
                                    "metric_resolved": metric_resolved})
                graph = graph_compile(name, graph_object, target_vars)
                if len(graph) > 0:
                    graphs.append(graph)
        # Graph Type #2: Carbon Match
        #   Metrics reported directly by carbon server to itself
        elif ("carbon_match" in graphsconf[name].keys() and
                graphsconf[name]["carbon_match"] and
                host == dashconf["carbon_match"]):
            graph_object = dict(graphsconf[name])
            del graph_object["carbon_match"]
            target_vars.update({"host": dashconf["carbon_server"],
                                "metric": name})
            graph = graph_compile(name, graph_object, target_vars)
            if graph:
                graphs.append(graph)
    return graphs


def graph_compile(name, graph_object, target_vars):
    """Finish compiling graph."""
    # Graphs consist of 3 parts
    #   1. graph_targets
    #   2. graph_object
    #   3. graph_render
    # target
    templates = graph_object.pop("target")
    target_object = list()
    target_pairs = list()
    for template in templates:
        template = string.Template(template)
        try:
            target = template.substitute(target_vars)
        except KeyError as e:
            field = e.args[0]
            log.debug("    (required field \"%s\" not found)" % field)
            return None
        target_object.append(target)
        target_pairs.append(("target", target))
    graph_targets = urllib.urlencode(target_pairs)
    # title
    if "title" in graph_object:
        template = string.Template(graph_object["title"])
        graph_object["title"] = template.substitute(target_vars)
    else:
        graph_object["title"] = name
    graph_object["title"] = graph_object["title"].replace("-", "_")
    graph_object["title"] = graph_object["title"].replace("*", "")
    graph_object["title"] = graph_object["title"].replace("?", "")
    # build graph_render
    graph_render = "/render?%s&%s" % (urllib.urlencode(graph_object),
                                      graph_targets)
    # add target(s) to graph_object
    graph_object["target"] = target_object
    return [graph_targets, graph_object, graph_render]


def dash_save(dash):
    """Save dashboard using Graphite libraries."""
    # Graphite libraries
    sys.path.append(dashconf["webapp_path"])
    os.environ["DJANGO_SETTINGS_MODULE"] = "graphite.settings"
    from graphite.dashboard.models import Dashboard
    dash_name = dash["name"]
    dash_state = str(json.dumps(dash))
    try:
        dashboard = Dashboard.objects.get(name=dash_name)
    except Dashboard.DoesNotExist:
        dashboard = Dashboard.objects.create(name=dash_name, state=dash_state)
    else:
        dashboard.state = dash_state
        dashboard.save()


def merge_dicts(dict_weak, dict_strong):
    """Merge two dictionaries--the values of the 2nd (dict_strong) overwrite
    the values of the 1st (dict_weak).
    """
    if isinstance(dict_weak, dict) and isinstance(dict_strong, dict):
        for key, value in dict_weak.iteritems():
            if key not in dict_strong:
                dict_strong[key] = value
            else:
                dict_strong[key] = merge_dicts(dict_strong[key], value)
    return dict_strong


def set_log_level(args):
    global log
    """Set the logging level."""
    loglevel = args.verbose - args.quiet
    if loglevel >= 2:
        log.setLevel(logging.DEBUG)
    elif loglevel == 1:
        log.setLevel(logging.INFO)
    elif loglevel == 0:
        log.setLevel(logging.WARN)
    elif loglevel < 0:
        log.setLevel(logging.CRITICAL)


def parser_setup():
    """Instantiate, configure, and return an argarse instance."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="count", default=1,
                    help="Print copious debugging info.")
    ap.add_argument("-q", "--quiet", action="count", default=0,
                    help="Suppress output. -qq to suppress ALL output.")
    # unable to define default for files due to
    # http://bugs.python.org/issue16399
    ap.add_argument("-f", "--file", dest="files", metavar="FILE_GLOB",
                    action="append", nargs="*",
                    help="Configuration file globs. May be specified multiple "
                         "times. (Default: \"*.y*ml\")")
    ap.add_argument("-H", "--host", dest="hosts", metavar="HOST_GLOB",
                    action="append", nargs="*",
                    help="Host globs for per_host dashboards. May be "
                         "specified multiple times.")
    args = ap.parse_args()
    if args.files:
        args.files = list(chain.from_iterable(args.files))
    else:
        args.files = ["*.y*ml", ]
    if args.hosts:
        args.hosts = list(chain.from_iterable(args.hosts))
    return args


def main():
    global dashconf, graphsconf
    # Command Line Options
    args = parser_setup()
    set_log_level(args)

    # Read YAML configuration files. A single namespace is used
    for conf_glob in args.files:
        for conf_path in glob.iglob(conf_glob):
            conf_file = os.path.basename(conf_path)
            conf_root = os.path.splitext(conf_file)[0]
            # dash only configs
            if conf_root.endswith("_dash"):
                dashconf = merge_dicts(dashconf,
                                       yaml.safe_load(open(conf_path)))
            # graphs only configs
            elif conf_root.endswith("_graphs"):
                graphsconf = merge_dicts(graphsconf,
                                       yaml.safe_load(open(conf_path)))
            # combined configs
            else:
                file_dict = yaml.safe_load(open(conf_path))
                # dash
                if "dash" in file_dict:
                    dashconf = merge_dicts(dashconf, file_dict["dash"])
                    log.debug("Merged Dash     configuration from: %s" %
                              conf_file)
                    del file_dict["dash"]
                # defaults
                if "defaults" in file_dict:
                    dashconf["defaults"] = merge_dicts(dashconf["defaults"],
                                                       file_dict["defaults"])
                    log.debug("Merged Defaults configuration from: %s" %
                              conf_file)
                    del file_dict["defaults"]
                # graphs
                if "graphs" in file_dict:
                    graphsconf = merge_dicts(graphsconf, file_dict["graphs"])
                    log.debug("Merged Graphs   configuration from: %s" %
                              conf_file)
                    del file_dict["graphs"]
                # dash
                dashconf = merge_dicts(dashconf, file_dict)
                log.debug("Merged Dash     configuration from: %s" % conf_file)
    if not dashconf:
        log.error("No dash definition found. A configuration file containing "
                  "a dash definition must be loaded.")
        sys.exit(1)
    if not graphsconf:
        log.error("No graph definitions found. A configuration file "
                  "containing graph definitions must be loaded.")
        sys.exit(1)

    # Per Group Graphs
    if dashconf["type"] == "per_group":
        for group in dashconf["groups"]:
            dash_name = "%s%s" % (dashconf["name_prefix"], group)
            dash = dash_create(dash_name)
            dash["graphs"] = per_group_graph_create(group)
            dash_save(dash)

    # Per Host Graphs
    if dashconf["type"] == "per_host":
        if not args.hosts:
            log.error("One or more HOST_GLOBs must be specified for per_host "
                      "dashboards")
            sys.exit(1)
        # Build hosts list
        host_parent_glob = "%s/%s" % (dashconf["whisper_path"],
                                      dashconf["source_glob"])
        host_paths = set()
        for host_glob in args.hosts:
            for host_path in glob.iglob("%s/%s" % (host_parent_glob,
                                                   host_glob)):
                host_path = os.path.abspath(host_path)
                if os.path.isdir(host_path):
                    host_paths.add(host_path)
        host_paths = list(host_paths)
        host_paths.sort()
        for host_path in host_paths:
            host = os.path.basename(host_path)
            dash_name = "%s%s" % (host, dashconf["name_suffix"])
            dash = dash_create(dash_name)
            dash["graphs"] = per_host_graph_create(host, host_path)
            dash_save(dash)


if __name__ == "__main__":
    main()
