#!/usr/bin/env python

from pyatem.protocol import AtemProtocol
from SuperSourceFuncs import SuperSourceCommand

import SuperSourceFuncs
import AtemServerComm

import time
import threading
import logging
from functools import partial


#switcher.state["me"] = 0  # TODO: Read from config

class AtemConnection(threading.Thread):
    def __init__(self, callback):
        self.callback_ = callback
        threading.Thread.__init__(self)
        self.name = 'Connection'
        self.ip = None
        self.connected_ = False
        self.log_ = logging.getLogger('AtemConnection')

    def run(self):
        if(self.ip is not None):
            try:
                self.switcher_ = AtemProtocol(self.ip)
                self.switcher_.state = {}
                self.switcher_.on("change", self.do_callback)   
                self.switcher_.connect()
            except ConnectionError as e:
                self.log_.error("Could not connect", e)
            while True:
                try:
                    self.switcher_.loop()
                except Exception as e:
                    self.log_.error(repr(e))
        else:
            self.log_.error("Only IP connections supported. Set IP before calling run")

    def do_callback(self, *args, **kwargs):
        self.callback_(self.switcher_, *args, **kwargs)
        
def handle_state_change(switcher, field, data):
    if field == "preview-bus-input":
        switcher.state["preview_source"] = data.source
    elif field == "program-bus-input":
        switcher.state["program_source"] = data.source

import socket
class CommandServer(threading.Thread):
    def __init__(self, host, port):
        self.host_ = host
        self.port_ = port
        self.commands_ = {}
        self.log = logging.getLogger('CommandServer')
        threading.Thread.__init__(self)

    def add_command(self, command, callback):
        self.commands_[command] = callback
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.host_, self.port_))
            self.log.info("listening on " + self.host_ + ":" + str(self.port_))
            while(True):
                data = s.recvfrom(1024)
                if not data:
                    self.log.warning("No data")
                end = data[0].find(b"\0", 0)
                num_args = int(data[0][0:end])
                start = end + 1
                end = data[0].find(b"\0", start)
                command = str(data[0][start:end].decode())
                args = []
                for arg in range(0, num_args):
                    start = end + 1
                    end = data[0].find(b"\0", start)
                    arg = data[0][start:end]
                    args.append(arg)
                self.commands_[command](*args)

if __name__ == "__main__":
    print("Starting ATEM Server")
    logging.basicConfig(level=logging.INFO)

    conn = AtemConnection(handle_state_change)
    conn.ip = "192.168.255.130"
    conn.deamon = True
    conn.start()

    handle = AtemServerComm.create()
    SuperSourceFuncs.load_layouts("ss_conf.json")

    server = CommandServer("127.0.0.1", 65432)
    server.deamon = True
    server.add_command("NextSSLayout", partial(SuperSourceFuncs.NextSSLayout, conn.switcher_, 0))
    server.add_command("PrevSSLayout", partial(SuperSourceFuncs.PrevSSLayout, conn.switcher_, 0))
    server.add_command("RecallSSLayout", partial(SuperSourceFuncs.RecallSSLayout, conn.switcher_, 0))
    server.add_command("StoreSSLayout", partial(SuperSourceFuncs.StoreSSLayout, conn.switcher_, 0))
    server.add_command("AssignSourceToSSBox", partial(SuperSourceFuncs.StoreSSLayout, conn.switcher_, 0))
    server.start()
    
    while True:
        time.sleep(1)
    
    
