global_settings = {
    "animation": {
        "type": 0,
        "frequency": 20
    },

    "supersource": {
        "current_layout": 0,
        "layouts": [],
        "layout_storage": [None]*4
    }
}

def get(key, conf=global_settings):
    try:
        i = key.index(":")
        return get(key[i+1:], conf[key[0:i]])
    except ValueError:
        return conf[key]
    except KeyError:
        print("Unknown settings key", key[0:i])

def set(key, value, conf=global_settings):
    try:
        i = key.index(":")
        set(key[i+1:], value, conf[key[0:i]])
    except ValueError:
        conf[key] = value
    except KeyError:
        print("Unknown settings key", key[0:i])
