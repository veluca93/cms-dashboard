#!/usr/bin/env python2

from config import config

class BaseHandler(object):
    def __init__(self):
        self.notify = None
        self.get_error = None

    def error_handler(self, data, addr):
        if self.get_error is not None:
            self.get_error(data, addr)
        print "Received error from %s:" % (addr,), 
        if data['msg'] == "invalidrequest":
            print "Invalid request."
        elif data['msg'] == "unauthorized":
            print "Unauthorized."
        elif data['msg'] == "exception":
            print "Raised exception"
            print data['traceback']
        else:
            print data['msg']

    def start(self, comm):
        if self.notify is not None:
            for n in self.notify:
                comm.send({"password": config.password, "action": "notify", "msg": "started"}, n)

    def __call__(self, data, addr):
        try:
            msgid = None
            act = data['action']
            if act == "error":
                self.error_handler(data, addr)
                return (None, False)
            del data['action']
            hdl = getattr(self, act + '_handler')
        except (AttributeError, KeyError):
            return ({"action": "error", "msg": "invalidrequest"}, False)
        try:
            assert(config.password == data['password'])
            del data['password']
        except:
            raise ({"action": "error", "msg": "unauthorized"}, False)
        try:
            ret = hdl(data, addr)
            if ret is None:
                return (None, False)
            return ret
        except:
            return ({"action": "error", "msg": "exception", "traceback": traceback.format_exc()}, False)
