#!/usr/bin/env python2
import errno
import json
import socket
import select
import traceback
import threading

class Communication(object):
    def __init__(self, addr, port, handler):
        self.port = port
        self.handler = handler
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        self.server_socket.bind((socket.gethostbyname(addr), port))
        self.server_socket.listen(5)
        self.received = dict()
        self.addr = dict()
        self.msgid = 0
        self.msgid_lock = threading.Lock() # Lock for operations on msgid

    def send(self, data, addr, port=None):
        if port is None:
            port = self.port
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.msgid_lock.acquire(True)
        data["__msgid"] = self.msgid
        self.msgid += 1
        self.msgid_lock.release()

        status = skt.connect((socket.gethostbyname(addr), port))
        skt.sendall(json.dumps(data))

    def answer(self, data, addr):
        try:
            answer = self.handler(data, addr)
            if answer is not None:
                self.send(answer, addr[0])
        except:
            traceback.print_exc()

    def run(self):
        self.handler.start(self)
        while True:
            try:
                print "Starting select...", [self.server_socket] + self.received.keys(), self.received.keys()
                skt_in, skt_out, skt_err = select.select([self.server_socket] + self.received.keys(), [], self.received.keys(), 10)
                print "Ending select...", skt_in, skt_out, skt_err
                print "Handling errors"
                for s in skt_err:
                    if s in self.to_send:
                        s.close()
                        del self.to_send[s]
                    if s in self.received:
                        s.close()
                        del self.received[s]
                print "Handling input"
                for s in skt_in:
                    if s is self.server_socket:
                        skt, client_addr = s.accept()
                        skt.setblocking(0)
                        self.received[skt] = []
                        self.addr[skt] = client_addr
                    else:
                        data = s.recv(4096)
                        if data:
                            self.received[s] = [data]
                        else:
                            t = threading.Thread(target=self.answer, args=(json.loads(''.join(self.received[s])), self.addr[s]))
                            t.daemon = True
                            t.start()
                            s.close()
                            del self.received[s]
                            del self.addr[s]
            except KeyboardInterrupt:
                return 0
            except:
                traceback.print_exc()
