import threading
import logging
import asyncio
import websockets
import command
import json
from functools import partial

class CommandServer(threading.Thread):
    def __init__(self, host, port, atem_conns=[]):
        self.host_ = host
        self.port_ = port
        self.commands_ = {}
        self.log = logging.getLogger('CommandServer')
        threading.Thread.__init__(self)
        self.loop = asyncio.get_event_loop()
        self.atem_connections_ = atem_conns
        for module in command.modules:
            print("INITIALIZING", module)
            for conn in self.atem_connections_:
                command.modules[module]["init"](conn)

    feedback_providers = {}
    @staticmethod
    def register_feedback_provider(module, fun):
        print("REGISTER FEEDBACK FUNCTION", module, fun)
        CommandServer.feedback_providers[module] = fun
        
    def add_command(self, command, callback):
        self.commands_[command] = callback
    
        if field not in self.event_handlers_:
            self.event_handlers_[field] = []
        self.event_handlers_[field].append(cbk)

    async def send_feedback(self):
        rets = {}
        for module in command.modules:
            rets[module] = CommandServer.feedback_providers[module]()
        await self.websocket.send(json.dumps(rets))
            
    def atem_status_changed(self, atem_conn, field, data):
        asyncio.run(self.send_feedback())
        
    async def handle_connection(self, websocket):
        print("CONNECTION")
        global command
        self.websocket = websocket
        for conn in self.atem_connections_:
            conn.register_on_change_handler("*", self.atem_status_changed)
        
        for module in command.modules:
            print("FEEDBACK", module)
            await self.send_feedback()
            
        while True:
            data = None
            try:
                data = await websocket.recv()
            except asyncio.IncompleteReadError as e:
                print("INCOMPLETE READ", e)
                continue
            if not data:
                self.log.warning("No data")
                pass 
            data = data.strip()
            
            parts = data.split(" ")
            cmd_parts = parts[0].split(".")
            if len(cmd_parts) > 1:
                module = cmd_parts[0]
                cmd = cmd_parts[1]
                args = []
                if len(parts) > 1:
                    args = parts[1:]
                ret = {}
                ret[module] = command.modules[module]["cbks"][cmd](*args)
                if ret is not None:
                    await websocket.send(json.dumps(ret))

    async def serve(self):
        async with websockets.serve(self.handle_connection, "localhost", 65432):
            await asyncio.Future()

    def run(self):
        asyncio.run(self.serve())
