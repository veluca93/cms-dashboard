#!/usr/bin/env python2

from config import config
from communication import Communication

def handle(addr, data):
    print data, addr
#    return data

comm = Communication(config["listen"], config["port"], handle)
comm.run()
