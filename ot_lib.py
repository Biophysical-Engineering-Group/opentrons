import os
import sys
import json
import getpass

def get_lw_name(def_file:str) -> str:
    with open(def_file, 'r') as f:
        return(json.load(f)["parameters"]["loadName"])

def get_script_path() -> str:
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def create_metadata(proto_name:str, source_script:str, u_name:str=getpass.getuser()) -> str:
    if u_name == '':
        u_name = getpass.getuser()

    return (f"""
metadata = {{
    'protocolName' : \'{proto_name}\',
    'author' : \'{u_name}\',
    'source' : \'{source_script}\',
    'apiLevel' : '2.3'
}}
""")