import os
import sys
import json

def get_lw_name(def_file):
    with open(def_file, 'r') as f:
        return(json.load(f)["parameters"]["loadName"])

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))