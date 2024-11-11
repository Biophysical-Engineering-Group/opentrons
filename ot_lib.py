import os
import sys
import json
import getpass
from typing import List

def get_lw_name(def_file:str) -> str:
    """
    Get the loadName parameter associated with a piece of labware

    Parameters:
        def_file (str) : The labware definition file
    
    Returns:
        (str) : The name of the labware used by the Opentrons
    """
    with open(def_file, 'r') as f:
        return(json.load(f)["parameters"]["loadName"])
    
def get_well_volumes(def_file:str, wells:List[str]=[]) -> str:
    """
    Get the volumes of a set of wells from the labware definition file
    Parameters:
        def_file (str) : The labware definition file
        wells (List[str]) : (optional) A list of wells to get the volumes for.  If not provided, returns all wells.

    Returns:
        (List[float]) : The volume of each well
    """
    volumes = []
    with open(def_file, 'r') as f:
        data = json.load(f)
        
        if wells == []:
            wells = list(data['wells'].keys())

        for w in wells:
            volumes.append(data['wells'][w]['totalLiquidVolume'])
    
    return volumes

def get_script_path() -> str:
    """
    Get the parent directory of the currently running script
    Returns:
        (str) : The path to the script directory
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def create_metadata(proto_name:str, source_script:str, u_name:str=getpass.getuser()) -> str:
    """
    Create a metadata entry for the run script
    Parameters:
        proto_name (str) : The display name of the protocol in the Opentrons app
        source_script (str) : The name of the script that generates the run script
        u_name (str) : The name of the user who created the script
    Returns:
        (str) : A formatted metadata string to append to the run script
    """
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