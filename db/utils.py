from datetime import datetime

class Singleton(type):
    """
    A class to create singleton instance

    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def generate_keys_counter(counter_dict):
    temp = {}
    for c_key in counter_dict:
        non = counter_dict[c_key]['Nonline']
        noff = counter_dict[c_key]['Noffline']
        slot_len = len(counter_dict[c_key]['slots'])
        temp["{}/NONPH".format(c_key)] = int(non/slot_len)
        temp["{}/NOFFPH".format(c_key)] = int(noff/slot_len)
        for s in counter_dict[c_key]['slots']:
            temp["{}/slot/{}/NONCUR".format(c_key, s)] = 0
            temp["{}/slot/{}/NOFFCUR".format(c_key, s)] = 0
        temp["{}/type".format(c_key)] = counter_dict[c_key]['type']
        temp["{}/ttl".format(c_key)] = counter_dict[c_key]['TTL']
    return temp

def generate_keys_clerk(branch_id, clerk_dict):
    temp = {}
    for c_key in clerk_dict:
        temp["{}/clerk/{}".format(branch_id, c_key)] = clerk_dict[c_key]['counter_id']
    return temp

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '/')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '/')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def how_many_seconds_until_midnight():
    """Get the number of seconds until midnight."""
    n = datetime.now()
    return ((24 - n.hour - 1) * 60 * 60) + ((60 - n.minute - 1) * 60) + (60 - n.second) 