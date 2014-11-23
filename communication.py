#!/usr/bin/env python2
import errno
import json
import socket
import select
import traceback
import threading

#TODO: crypt with AES or something similar

class Communication(object):
    def __init__(self, addr, port, handler):
        self.port = port
        self.handler = handler
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostbyname(addr), port))
        self.server_socket.listen(5)

    def __send(self, data, skt):
        skt.sendall(json.dumps(data))

    def __recv(self, skt):
        data = skt.makefile().readline()
        data = json.loads(data)
        return data

    def run_in_thread(self, fun, args):
        t = threading.Thread(target=fun, args=args)
        t.daemon = True
        t.run()

    def send(self, data, addr, port=None):
        if port is None:
            port = self.port

        def real_send(data, addr, port):
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            status = skt.connect((socket.gethostbyname(addr), port))
            self.__send(data, skt)
            self.answer(skt)

        self.run_in_thread(real_send, (data, addr, port))

    def answer(self, skt):
        while(True):
            try:
                #TODO: timeouts?
                try:
                    addr = skt.getpeername()
                    data = self.__recv(skt)
                except:
                    if addr is not None:
                        print "Invalid data from", addr
                        raise
                if data is not None:
                    answer = self.handler(data, addr)
                else:
                    answer = (None, False)
                if answer[0] is not None:
                    self.__send(answer, skt)
                if answer[1] is False:
                    skt.close()
                    break
            except:
                traceback.print_exc()
                self.__send({"action": "error", "msg": "invalidrequest"}, skt)
                skt.close()
                return

    def run(self):
        self.handler.start(self)
        while True:
            try:
                s = self.server_socket.accept()
                print "New connection from", s[1]
                self.run_in_thread(self.answer, [s[0]])
            except KeyboardInterrupt:
                break
            except:
                traceback.print_exc()
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()
