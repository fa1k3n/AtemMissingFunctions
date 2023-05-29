#!/usr/bin/env python

from pyatem.protocol import AtemProtocol
from SuperSourceFuncs import SuperSourceCommand

import CommandServer

import SuperSourceFuncs
import USKFuncs

import time
import threading
import logging
from functools import partial
import copy
import argparse

class AtemConnection(threading.Thread):
    def __init__(self, ip=None):
        global state
        threading.Thread.__init__(self)
        self.name = 'Connection'
        self.ip_ = ip
        self.connected_ = False
        self.log_ = logging.getLogger('AtemConnection')
        self.handlers_ = {"change": {'*': []}}

    def run(self):
        if(self.ip_ is not None):
            try:
                self.switcher_ = AtemProtocol(self.ip_)
                self.switcher_.on("change", self.handle_on_change)

                self.switcher_.on("change:preview-bus-input:*", self.handle_preview_bus_input)
                self.switcher_.on("change:program-bus-input:*", self.handle_program_bus_input)
                self.switcher_.on("change:key-properties-base:*", self.handle_key_properties_base)
                
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

    def register_on_change_handler(self, field, cbk):
        print("ON CHANGE HANDLER", field)
        if field not in self.handlers_["change"]:
            self.handlers_["change"][field] = []
        self.handlers_["change"][field].append(cbk)

    def subscribe(self, variable, cbk):
        #var = self.state_.get_variable(variable)
        #var.subscribe(cbk)
        pass
    
    def handle_preview_bus_input(self, data, **argv):
        print("PREVIEW CHANGE", data.index, data.source)
        #if len(self.state_.state_) > 0:
        #    print("CACHE", self.state_.state_["0"])
        #var = self.state_.get_variable(str(data.index) + ".preview_bus_input")
        #print("PREVIOUS", var)
        #var.value = data.source
        
    def handle_program_bus_input(self, data, **argv):
        print("PROGRAM CHANGE", data.index, data.source)
        #self.state_.get_variable(str(data.index) + ".program_bus_input").value = data.source

    def handle_key_properties_base(self, data, **argv):
        print("KEY Properties", data)
        #var = self.state_.get_variable(str(data.index) + ".key_properties_base")
        #ret = copy.deepcopy(var.value)
        #if ret is None:
        #    ret = [{"key_source": None, "fill_source": None}]*4
        #ret[data.index]["key_source"] = data.key_source
        #ret[data.index]["fill_source"] = data.fill_source
        #var = ret
        
        #self.state_.get_variable(data.index, "program_bus_input").set(data.source)
        
    def handle_on_change(self, field, data):
        cbks = []
        if field in self.handlers_["change"]:
            cbks.extend(self.handlers_["change"][field])
        cbks.extend(self.handlers_["change"]["*"])
        for cbk in cbks:
            cbk(self, field, data)
            
        #if field == "preview-bus-input":
        #    self.handle_preview_bus_input(field, data)
        #elif field == "program-bus-input":
        #    self.handle_program_bus_input(field, data)
            #self.switcher_.state["program_source"] = data.source
        
if __name__ == "__main__":
    print("Starting ATEM Server")
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog='AtemServer',
        description='Animated Super Source, ALPHA'
        )
    parser.add_argument("atem_ip")
    args = parser.parse_args()
    conn = AtemConnection(args.atem_ip)
    conn.start()

    SuperSourceFuncs.load_layouts("ss_conf.json")

    server = CommandServer.CommandServer("127.0.0.1", 65432, [conn])
    server.deamon = True
    server.start()
    
    while True:
        time.sleep(1)
    
    
