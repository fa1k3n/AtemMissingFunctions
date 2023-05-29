import time
from datetime import datetime

LINEAR = 0
EASE_IN_OUT = 1
BOUNCE = 2

def get_animation_factor(current_frame, total_frames, animation_type):
    # For linear animation just leave the factor as is 
    factor = (current_frame + 1) / total_frames
    if(animation_type == EASE_IN_OUT):
        factor_s = factor ** 2
        factor = factor_s / (2.0 * (factor_s - factor) + 1.0)
    elif(animation_type == BOUNCE):
        factor = factor * factor * (4.0 - 3.0 * factor)
    return factor

def get_frame(start, end, frame, total_frames, animation_type):
    factor = get_animation_factor(frame, total_frames, animation_type)
    return start + factor * (end - start)
                

class Animator:
    def __init__(self, duration=1, animation_type=LINEAR, update_frequency=20):
        self.update_frequency_ = update_frequency
        self.current_frame_ = 0
        self.animation_type_ = animation_type
        self.total_frames_ = int(self.update_frequency_ * duration)
        self.time_per_step_ = 1 / self.update_frequency_
        
    def start(self, values, frame_cbk):
        start = time.time()
        now = datetime.now()
        for frame in range(1, self.total_frames_+1):
            t1 = time.time()
            self.current_frame_ = frame
            ret_vals = []
            for value in values:
                grp_values = []
                for param in value:
                    next_value = self.get_frame(param[0], param[1])
                    grp_values.append(next_value)
                ret_vals.append(grp_values)
            frame_cbk(ret_vals)
            delta = time.time() - t1
            if self.time_per_step_ > delta:
                time.sleep(self.time_per_step_ - delta)
        
    def get_animation_factor_(self):
        # For linear animation just leave the factor as is 
        factor = self.current_frame_ / self.total_frames_
        if(self.animation_type_ == EASE_IN_OUT):
            factor_s = factor ** 2
            factor = factor_s / (2.0 * (factor_s - factor) + 1.0)
        elif(self.animation_type_ == BOUNCE):
            factor = factor * factor * (4.0 - 3.0 * factor)
        return factor

    def get_frame(self, start, end):
        factor = self.get_animation_factor_()
        return start + factor * (end - start)
