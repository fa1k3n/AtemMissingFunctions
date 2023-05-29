import CommandServer

modules = {}

def registerCommandModule(name, desc):
    print("Register command module", name)
    modules[name] = {
        "description": desc
    }
    
def Command(module=None):
    global modules
    def inner_cmd(func):
        if module is not None:
            if "cbks" not in modules[module]:
                modules[module]["cbks"] = {}
            modules[module]["cbks"][func.__name__] = func
            print("Register func", module + ":" + func.__name__)
        def inner_func():
            return func()
        return inner_func
    return inner_cmd

def Feedback(module=None):
    def inner_cmd(func):
        if module is not None:
            CommandServer.CommandServer.register_feedback_provider(module, func)
            #if "feedbacks" not in modules[module]:
            #    modules[module]["feedbacks"] = []
            #modules[module]["feedbacks"].append(func)
            #print("Register feedback", module + ":" + func.__name__)
        def inner_func(*args):
            return func(*args)
        
        return inner_func
    
    return inner_cmd

def Init(module=None):
    global modules
    def inner_cmd(func):
        if module is not None:
            modules[module]["init"] = func 
            print("Register init", module + ":" + func.__name__)
        def inner_func():
            return func()
        return inner_func
    return inner_cmd
