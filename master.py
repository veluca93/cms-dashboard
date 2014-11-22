#!/usr/bin/env python2

from config import config
from communication import Communication
from basehandler import BaseHandler

class Master(BaseHandler):
    def notice_handler(self, data, addr):
        print data, addr

comm = Communication(config["listen"], config["port"], Master())
comm.run()
