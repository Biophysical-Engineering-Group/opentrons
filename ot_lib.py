import os
import sys
import json
import getpass
from typing import List, Dict

def read_excel(excel_file:str) -> Dict[str, List]:
    if excel_file.endswith('.xls'):
        import xlrd
        sheet = xlrd.open_workbook(excel_file).sheet_by_index(0)
        cols = [sheet.col_values(colx) for colx in range(sheet.ncols)]
    elif excel_file.endswith('.xlsx'):
        import openpyxl
        sheet = openpyxl.load_workbook(excel_file, data_only=True).active
        cols = list(sheet.iter_cols(values_only=True))
    elif excel_file.endswith('.csv'):
        with open(excel_file, 'r') as f:
            rows = [r.split(',') for r in f.readlines()]
            cols = list(map(list, zip(*rows)))
    else:
        raise(RuntimeError("File {excel_file} does not appear to be an Excel file (should end in xls, xlsx or csv)"))
    
    output = {cols[i][0].lower() : list(cols[i][1:]) for i in range(len(cols))}
    output['row numbers'] = list(range(2, len(output['source well'])+2))

    return output

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
    
def get_well_volumes(def_file:str, wells:List[str]=[]) -> List[float]:
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
    'apiLevel' : '2.20'
}}
""")