import sys, os
import tempfile
import random
import string
import json
import argparse
from hyperopt import STATUS_OK, STATUS_FAIL


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from dreamplace.Params import Params
from dreamplace.hyperoptim import HyperOptim

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
        
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs',type=int, default=100, help='number of iterations')
    parser.add_argument('--file', type=str, help='pt file which contains Data', required=True)
    parser.add_argument('--out', type=str, help='the directory path for output', default='./bo_results')

    args = parser.parse_args()
    return args

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
    return {'loss':hpwl, 'status': STATUS_OK if found else STATUS_FAIL}

if __name__ == '__main__':
    args = parse_args()
    saved_dir=args.out
    param_path = args.file
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)
    
    params = Params()
    params.load(param_path)
    bo = HyperOptim(params, place_wrapper,saved_dir)
    bo.run_BO(args.runs)
    bo.save(saved_dir)
        
          
