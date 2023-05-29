#from AtemServer import CommandServer
import command

from pyatem.protocol import AtemProtocol
from pyatem.command import KeyTypeCommand
from pyatem.command import KeyFillCommand

import struct

usk_data = [0, 0, 0, 0]
usk_type_name_map = ["Luma", "Chroma", "Pattern", "DVE"]
pvw_source = None
pgm_source = None
switcher = None
me = 0

command.registerCommandModule("USK", "Commands for controlling USK functionallity")

@command.Feedback("USK")
def feedback(handler=None):
    ret = []
    for data in usk_data:
        ret.append(usk_type_name_map[data])
    return ret

def handle_key_properties_changed(atem_conn, field, msg):
    global usk_data
    print("Key properties changed", msg.index, msg.keyer, msg.type)
    usk_data[msg.keyer] = msg.type

def handle_preview_bus_input_changed(atem_conn, field, msg):
    global pvw_source
    pvw_source = msg.source

def handle_program_bus_input_changed(atem_conn, field, msg):
    global pgm_source
    pgm_source = msg.source

def test(variable, value):
    print(variable, "just changed to", value)
    
@command.Init("USK")
def init(atem_conn):
    global switcher
    print("INIT USK")
    switcher = atem_conn.switcher_
    atem_conn.subscribe('0.preview-bus-input', test)
    atem_conn.subscribe('0.program-bus-input', test)
    atem_conn.register_on_change_handler("key-properties-base", handle_key_properties_changed)
    atem_conn.register_on_change_handler("preview-bus-input", handle_preview_bus_input_changed)
    atem_conn.register_on_change_handler("program-bus-input", handle_program_bus_input_changed)
    return feedback()

@command.Command("USK")
def AssignSourceToDVE(dve_index, source):
    if source == "pvw":
        source = switcher.state["preview_source"]
    elif source == "pgm":
        source = switcher.state["program_source"]
    else:
        source = int(source)

    print("AssignSourceToDVE", source, dve_index)
    cmd = KeyTypeCommand(me, int(dve_index), 3)
    switcher.send_commands([cmd])
    cmd = KeyFillCommand(me, int(dve_index), source)
    switcher.send_commands([cmd])

@command.Command("USK")
def ToggleUSKType(direction, usk_index):
    usk_index = int(usk_index)
    next_key = (usk_data[usk_index]  + 1) % len(usk_type_name_map)
    cmd = KeyTypeCommand(me, usk_index, next_key)
    switcher.send_commands([cmd])

@command.Command("USK")
def AssignFillSource(source, index):
    print("Assign fill source", index, source)
    if source == 'pvw':
        source = int(pvw_source)
    elif source == 'pgm':
        source = int(pgm_source)
    cmd = KeyFillCommand(me, int(index), source)
    switcher.send_commands([cmd])

@command.Command("USK")
def AssignKeySource(source, index):
    print("Assign key source", index, source)
    if source == 'pvw':
        source = int(pvw_source)
    elif source == 'pgm':
        source = int(pgm_source)
    cmd = KeyCommand(me, int(index), source)
    switcher.send_commands([cmd])
