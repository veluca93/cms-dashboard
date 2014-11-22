#!/usr/bin/env python2

from config import config

class BaseHandler(object):
    def __init__(self):
        self.notify = None

    def start(self, comm):
        if self.notify is not None:
            for n in self.notify:
                comm.send({"password": config.password, "action": "notify", "msg": "started"}, n)

    def __call__(self, data, addr):
        try:
            msgid = None
            act = data['action']
            msgid = data['__msgid']
            del data['action'], data['__msgid']
            hdl = getattr(self, act + '_handler')
        except (AttributeError, KeyError):
            ret = {"action": "notify", "msg": "invalid"}
        else:
            ret = hdl(data, addr)
        if ret is None:
            return None
        if msgid is not None:
            ret['__answers'] = msgid
        return ret
