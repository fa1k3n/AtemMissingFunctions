from pyatem.protocol import AtemProtocol
from pyatem.command import Command
import struct
import json
import threading
import time
import copy
import logging
import settings
import animation

import command

logger = logging.getLogger("SuperSourceFuncs")

def load_layouts(filename):
    logger.info("Loading layouts from " + filename)
    conf = {}
    with open(filename, "r") as confstream:
        conf = json.load(confstream)
     
    if "layouts" not in settings.get("supersource"):
        logger.warning("Creating layout section in settings")
        settings.set("supersource:layouts", [])

    layouts = []
    for layout in conf["layouts"]:
        logger.debug("Found layout" + str(layout))
        layouts.append(layout)
    settings.set("supersource:layouts", layouts)

def get_box_in_layout(layout_no, box_no):
    if layout_no == None:
        return None
    for box in settings.get("supersource:layouts")[layout_no]["config"]:
        if box[0] == box_no:
            return box
    return None

def is_fullscreen_layout(layout_no):
    if layout_no == None:
        return False

    fullscreen = False
    for box in global_settings["supersource"]["layouts"][layout_no]["config"]:
        if box[1] == 1:
            fullscreen = True

    # TODO: Check if higher number boxes are overlapping
    return fullscreen       

def get_active_boxes(layout_no):
    boxes = []
    if layout_no is not None:
        conf = settings.get("supersource:layouts")
        for box in conf[layout_no]["config"]:
            boxes.append(box[0])
    return boxes

def box_in_list(box_no, box_list):
    for box in box_list:
        if box[1] == box_no:
            return True
    return False
        
def animate_transition(switcher, me, current_state, end_state, duration):
    anim_freq = settings.get("animation:frequency")
    animator = animation.Animator(duration, animation.EASE_IN_OUT, anim_freq)

    def update_atem(values):
        cmds = []
        for val in values:
            cmds.append(SuperSourceCommand(me=me, box=int(val[0]), enable=1, size=val[1], xpos=val[2], ypos=val[3], left_crop=val[4], right_crop=val[5], top_crop=val[6], bottom_crop=val[7]))
        switcher.send_commands(cmds)

    anim_data = []
    for index in range(0, 4):
        box_data = []
        if current_state[index] is None:
          continue
        for param in range(0, len(current_state[index])):
            box_data.append((current_state[index][param], end_state[index][param]))
        anim_data.append(box_data)
    animator.start(anim_data, update_atem)
    
def set_layout(switcher, me, layout_no, direction="forward"):
    current_layout = settings.get("supersource:current_layout")
    layouts = settings.get("supersource:layouts")
    unused_boxes = range(0, 4)
    
    start_boxes = get_active_boxes(current_layout)
    end_boxes = get_active_boxes(layout_no)
    active_boxes = start_boxes + list(set(end_boxes) - set(start_boxes))    

    current_state = [None]*4
    end_state = [None]*4

    for box in layouts[current_layout]["config"]:
        current_state[box[0]] = box.copy()
    for box in layouts[layout_no]["config"]:
        end_state[box[0]] = box.copy()
        
    # These are the boxes that are to be animated
    anim_boxes = []
    for box in layouts[current_layout]["config"]:
        anim_boxes.append(box.copy())
    for box in layouts[layout_no]["config"]:
        if box[0] not in start_boxes:
            anim_boxes.append(box.copy())
            
    cmds = []
    # Prepare for the animations
    for index in range(0, 4):
        if current_state[index] is None and end_state[index] is not None:
            current_state[index] = end_state[index].copy()
            box = current_state[index]
            # This box appears, Setup box to start outside picture
            if(direction == "forward"):
                box[3] = -27
            elif(direction == "reverse"):
                box[3] = 27
                
            switcher.send_commands([SuperSourceCommand(me=me, box=box[0], enable=1, size=box[1], xpos=box[2], ypos=box[3], left_crop=box[4], right_crop=box[5], top_crop=box[6], bottom_crop=box[7])])
        elif current_state[index] is not None and end_state[index] is None:
            # This box disappears
            end_state[index] = copy.deepcopy(current_state[index])
            if(direction == "forward"):
                end_state[index][3] = 27
            elif(direction == "reverse"):
                end_state[index][3] = -27 

    animate_transition(switcher, me, current_state, end_state, 0.5)

    # Disable unused boxes
    cmds = []
    unused_boxes = list(set([0, 1, 2, 3]) - set(end_boxes))
    for box in unused_boxes:
        cmds.append(SuperSourceCommand(me=me, box=box, enable=0))
    switcher.send_commands(cmds)
    settings.set("supersource:current_layout", layout_no)


command.registerCommandModule("SS", "Commands for SS functions")

atem_conn = None

@command.Init("SS")
def init(conn):
    global atem_conn
    atem_conn = conn

@command.Feedback("SS")
def feedback(hander=None):
    layouts = settings.get("supersource:layouts")
    storage = settings.get("supersource:layout_storage")
    ret = [""]*len(storage)
    for index, slot in enumerate(storage):
        if slot is not None:
            ret[index] = layouts[slot]["name"]
    return {"slots": ret}

@command.Command("SS")
def NextLayout():
    layout = settings.get("supersource:current_layout")
    layouts = settings.get("supersource:layouts")
    if layout == None:
        layout = 0
    else:
        layout = (layout + 1) % len(layouts)
    logger.debug("NextSSLayout:" + layouts[layout]["name"])
    set_layout(atem_conn.switcher_, 0, layout, direction="forward")

@command.Command("SS")
def PrevLayout():
    layout = settings.get("supersource:current_layout")
    layouts = settings.get("supersource:layouts")
    if layout == None:
        layout = 0
    else:
        if layout == 0:
            layout = len(layouts) - 1
        else:
            layout = (layout - 1) % len(layouts)
    logger.debug("PrevSSLayout:" + layouts[layout]["name"])
    set_layout(atem_conn.switcher_, 0, layout, direction="reverse")

@command.Command("SS")
def RecallLayout(slot_no):
    slot_no = int(slot_no) - 1
    print("RecallSSLayout", slot_no)
    layout = settings.get("supersource:layout_storage")[slot_no]
    if layout is not None:
        set_layout(atem_conn.switcher_, 0, layout)

@command.Command("SS")
def StoreLayout(slot_no):
    slot_no = int(slot_no) - 1
    layout = settings.get("supersource:current_layout")
    layouts = settings.get("supersource:layouts")
    print("StoreSSLayout", slot_no)
    settings.get("supersource:layout_storage")[slot_no] = layout
    return feedback()

@command.Command("SS")
def AssignSourceToBox(box, source):
    box = int(box)
    if source == "pvw":
        source = atem_conn.switcher_.state["preview_source"]
    elif source == "pgm":
        source = atem_conn.switcher_.state["program_source"]
    else:
        source = int(source)
    print("AssignSourceToSSBox", source, box)
    cmd = SuperSourceCommand(me=0, box=box, source=int(source))
    atem_conn.switcher_.send_commands([cmd])
        
class SuperSourceCommand(Command):
    def __init__(self, me=0, box=0, enable=None, source=None, xpos=None, ypos=None, size=None, left_crop=None, right_crop=None, top_crop=None, bottom_crop=None):
        self._me = me
        self._box = box
        self._enable = enable
        self._source = source
        self._xpos = xpos
        self._ypos = ypos
        self._size = size
        self._left_crop = left_crop
        self._right_crop = right_crop
        self._top_crop = top_crop
        self._bottom_crop = bottom_crop

    def decodeFlags(flags):
        flagStr = ""
    
        if flags & 0x1:
            flagStr += " ENABLED "
        else:
            flagStr += " DISABLED "

        return flagStr

    def get_command(self):
        #struct.pack('>BBBBHhhHBBHHHHBB', 0, me, box, box_flags, unknown_1, source, posX, posY, size, crop_flags, unknown_2, crop_top, crop_bottom, crop_left, crop_right, unknown_3, unknown_4)
        #data = bytearray([0x00, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x54, 0x2c, 0x8a, 0x17, 0x8c, 0x16, 0x1a, 0x38, 0xa8, 0xb4, 0x26, 0x7f, 0xf7, 0x00, 0x00])
        #                    FLAGS     ME    BOX   EN    ?     INPUT SRC      X POS      Y POS       SIZE     CROP   crop_top    crop_bot     crop_l     crop_r

        flags = 0x0
        enable = 0
        source = 0
        xpos = 0
        ypos = 0
        size = 0
        crop_enabled = 0
        top_crop = 0
        bottom_crop = 0
        left_crop = 0
        right_crop = 0
        if self._enable is not None:
            flags |= 0x01
            enable = self._enable
        if self._source is not None:
            flags |= 0x02
            source = self._source
        if self._xpos is not None:
            flags |= 0x04
            xpos = int(self._xpos * 100)
        if self._ypos is not None:
            flags |= 0x08
            ypos = int(self._ypos * 100)
        if self._size is not None:
            flags |= 0x10
            size = int(self._size * 1000)
        if self._top_crop is not None:
            flags |= 0x20
            flags |= 0x40
            crop_enabled = 1
            top_crop = int(self._top_crop * 1000)
        if self._bottom_crop is not None:
            flags |= 0x20
            flags |= 0x80
            crop_enabled = 1
            bottom_crop = int(self._bottom_crop * 1000)
        if self._left_crop is not None:
            flags |= 0x20
            flags |= 0x100
            crop_enabled = 1
            left_crop = int(self._left_crop * 1000)
        if self._right_crop is not None:
            flags |= 0x20
            flags |= 0x200
            crop_enabled = 1
            right_crop = int(self._right_crop * 1000)    
        
        data = struct.pack('>HBBBBHhhHBBHHHH', flags, self._me, self._box, enable, 0x7f, source, xpos, ypos, size, crop_enabled, 0xff, top_crop, bottom_crop, left_crop, right_crop)

        # FLAGS
        #    0x01  == ENABLED/DISABLED
        #    0x02  == SOURCE
        #    0x04  == X pos
        #    0x08  == Y pos
        #    0x10  == Size
        #    0x20  == Crop enable
        #    0x40  == Crop top
        return self._make_command('CSBP', data)
