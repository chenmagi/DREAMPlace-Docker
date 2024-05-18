from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import os,sys
from copy import copy
import tempfile
import random
import string
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from dreamplace.Params import Params

def apply_params(params, hyperparams:dict):
    new_params = copy(params)
    for key in ['num_bins_x', 'num_bins_y', 'target_density', 'density_weight']:
        new_params.__dict__[key] = hyperparams[key]
    
    for key in hyperparams.keys():
        new_params.__dict__['global_place_stages'][0][key]=hyperparams[key]
    
    return new_params

class Temp():
    def __init__(self):
        pass
    @staticmethod
    def get_tempfilename(suffix=''):
        fname=''.join(random.choice(string.ascii_lowercase) for _ in range(16))
        fname='%s%d-%s'%(fname, random.randint(1000,100000),suffix)
        fpath=os.path.join(tempfile.gettempdir(), fname)
        return fpath
    
    @staticmethod
    def remove_random_file(path:str):
        if not os.path.exists(path):
            return
        if os.path.dirname(path) == tempfile.gettempdir():
            os.remove(path)

def place_wrapper(params:Params):
    jsdata = params.toJson()
    arg_path=Temp.get_tempfilename(suffix='arg')
    rc_path=Temp.get_tempfilename(suffix='rc')
    with open(arg_path, 'w') as fp:
        json.dump(jsdata, fp)
    
    cmd_str='python dreamplace/Placer.py %s %s'%(arg_path, rc_path)  
    os.system(cmd_str)
    
    found=False
    hpwl = sys.float_info.max
    
    if os.path.exists(rc_path):
        with open(rc_path) as fp:
            result = json.load(fp)
            hpwl = result['hpwl']    
            if isinstance(hpwl, str):
                hpwl = float(hpwl)
        found=True
    
    Temp.remove_random_file(rc_path)
    Temp.remove_random_file(arg_path)
    return {'hpwl':hpwl, 'status': found }


# Create server
with SimpleXMLRPCServer(('0.0.0.0', 9090),
                        requestHandler=SimpleXMLRPCRequestHandler) as server:
    server.register_introspection_functions()

    # Define a function that we want to expose via RPC
    def add(data):
        return data['x'] + data['y']
    def place(hyperparams:dict):
        new_params = Params()
        new_params.fromJson(hyperparams)
        return place_wrapper(new_params)
        

    # Register the function with the server
    server.register_function(add, 'add')
    server.register_function(place, 'place')

    # Run the server's main loop
    print("Serving RPC server on port 9090")
    server.serve_forever()
