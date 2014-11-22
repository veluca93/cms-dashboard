#!/usr/bin/env python2

import json
import socket
import select
import traceback


class Communication(object):
    def __init__(self, addr, port, handle):
        self.port = port
        self.handle = handle
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        self.server_socket.bind((socket.gethostbyname(addr), port))
        self.server_socket.listen(5)
        self.to_send = dict()
        self.received = dict()
        self.addr = dict()

    def send(self, data, addr, port=None):
        if port is None:
            port = self.port
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setblocking(0)
        self.to_send[skt] = json.dumps(data)
        skt.connect((socket.gethostbyname(addr), port))

    def run(self):
        while True:
            try:
                skt_in, skt_out, skt_err = select.select(
                        [self.server_socket] + self.received.keys(),
                        self.to_send.keys(),
                        self.received.keys() + self.to_send.keys()
                    )
                for s in skt_err:
                    if s in self.to_send:
                        s.close()
                        del self.to_send[s]
                    if s in self.received:
                        s.close()
                        del self.received[s]
                for s in skt_in:
                    if s is self.server_socket:
                        skt, client_addr = s.accept()
                        skt.setblocking(0)
                        self.received[skt] = ''
                        self.addr[skt] = client_addr
                    else:
                        data = s.recv(4096)
                        if data:
                            self.received[s] += data
                        else:
                            try:
                                answer = self.handle(self.addr[s], json.loads(self.received[s]))
                            except:
                                traceback.print_exc()
                            if answer is not None:
                                self.send(answer, self.addr[s])
                            s.close()
                            del self.received[s]
                            del self.addr[s]
                for s in skt_out:
                    if len(self.to_send[s]):
                        sent = s.send(self.to_send[s])
                        self.to_send[s] = self.to_send[s][sent:]
                    else:
                        s.close()
                        del self.to_send[s]
            except KeyboardInterrupt:
                return 0
            except:
                traceback.print_exc()
