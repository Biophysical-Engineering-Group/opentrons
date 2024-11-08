import argparse
import shutil
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) # sorry, this is dumb but I didn't want to force you to install this as a package.
from ot_lib import get_lw_name, get_script_path # You need the above line to be able to import from the parent directory without installing it as a package

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument('plate_spreadsheet', type=str, help="xls or xlsx file containing 'Well Position' column.  Optionally, 'Mask', 'Target' and 'Volume'.")
    p.add_argument('source_lw', type=str, help="Source labware definition file")
    p.add_argument('source_slot', type=str, help="Source slot on the Opentron")
    p.add_argument('dest_lw', type=str, help="Destination labware definition file")
    p.add_argument('dest_slot', type=str, help="Destination slot on the Opentron")
    p.add_argument('outfile', type=str, help="The name of the output script")
    p.add_argument('-v', '--volume', type=str, help="Volume to pipette from all wells if not specified in the spreadsheet")
    return p

def main():
    p = parser()
    args = p.parse_args()

    if not args.outfile.endswith('.py'):
        args.outfile = args.outfile+'.py'

    # Load the first sheet of the Excel file
    if args.plate_spreadsheet.endswith('.xls'):
        import xlrd
        sheet = xlrd.open_workbook(args.plate_spreadsheet).sheet_by_index(0)
        rows = [sheet.row_values(rowx) for rowx in range(sheet.nrows)]
    elif args.plate_spreadsheet.endswith('.xlsx'):
        import openpyxl
        sheet = openpyxl.load_workbook(args.plate_spreadsheet).active
        rows = list(sheet.iter_rows(values_only=True))
    elif args.plate_spreadsheet.endswith('.csv'):
        with open(args.plate_spreadsheet, 'r') as f:
            rows = [r.split(',') for r in f.readlines()]
    else:
        raise(RuntimeError("File {args.plate_spreadsheet} does not appear to be an Excel file (should end in xls, xlsx or csv)"))

    # Separate the column names
    colnames = [n.lower() for n in rows[0]]
    rows = np.array(rows[1:])

    istrue = lambda s: s.lower() in ['true', '1', '1.0', 't', 'y', 'yes', 'yeah', 'yup', 'ja', 'richtig']

    # Mask out unwanted rows
    if 'mask' in colnames:
        maskcol = colnames.index('mask')
        mask = [istrue(r[maskcol]) for r in rows]
        rows = rows[mask]

    sourcecol = colnames.index('well position')
    sources = rows.T[sourcecol]

    if 'target' in colnames:
        destcol = colnames.index('target')
        dests = rows.T[destcol]
    else:
        dests = np.array(['A1']*len(rows))

    # Figure out how much to pipette from each well
    volcol = False
    if 'volume' in colnames:
        volcol = colnames.index('volume')
        vols = rows.T[volcol]
    if volcol and args.volume:
        raise(RuntimeError("Conflicting input!  Volume given in both spreadsheet and command line"))
    elif volcol:
        pass
    elif args.volume:
        vols = np.array([args.volume]*len(rows))
    else:
        raise(RuntimeError("No volume information provided!  Either add a volume column or specify -v <number>"))
    
    # Make sure everything makes sense
    if ('' in sources):
        raise(RuntimeError(f"There is an unmasked well with no Well Position!"))
    
    if ('' in dests):
        raise(RuntimeError(f"Wells {', '.join(sources[dests == ''])} have no destination"))
    
    if ('' in vols):
        raise(RuntimeError(f"Wells {', '.join(sources[vols == ''])} have no volume specified"))
    
    if (vols.astype(float) < 20).any() or (vols.astype(float) > 300).any():
        raise(RuntimeError(f"Volumes must be between 20 and 300 µl for a P300 pipette. Wells {', '.join(sources[((vols.astype(float) < 20) ^ (vols.astype(float) > 300))])} outside range."))


    source_lw = get_lw_name(args.source_lw)
    dest_lw = get_lw_name(args.dest_lw)

    # Generate run script
    # The number of escapes that required is...
    outfile = shutil.copy(os.path.join(get_script_path(), 'cherrypick.py'), args.outfile)
    with open(outfile, 'a') as f:
        f.write("'''\"")
        f.write("Source Labware,Source Slot,Source Well,Source Aspiration Height Above Bottom (in mm),Dest Labware,Dest Slot,Dest Well,Volume (in ul)\\\\n\\\n")
        for s, d, v in zip(sources, dests, vols):
            f.write(f"{source_lw},{args.source_slot},{s},1,{dest_lw},{args.dest_slot},{d},{v}\\\\n\\\n")
        f.write("\"''')\n")

if __name__ == '__main__':
    main()

    