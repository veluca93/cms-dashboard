#!/usr/bin/env python2

import yaml
import sys

def get_config():
    configpath = sys.argv[1] if len(sys.argv) > 1 else "/usr/local/etc/cms-dashboard.yaml"
    return yaml.load(open(configpath))


config = get_config()
