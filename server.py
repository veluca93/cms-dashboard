#!/usr/bin/env python2

from communication import Communication

def handle(addr, data):
    print data, addr
#    return data

comm = Communication("", 9000, handle)
comm.run()
