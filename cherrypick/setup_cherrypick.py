import argparse
import shutil
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) # sorry, this is dumb but I didn't want to force you to install this as a package.
from ot_lib import get_lw_name, get_script_path, create_metadata, get_well_volumes, read_excel # You need the above line to be able to import from the parent directory without installing it as a package
 
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument('instruction_spreadsheet', type=str, help="xls, xlsx, or csv file containing 'Source slot', 'Source Well', 'Target slot', and 'Target Well' columns.  Optionally, 'Mask' and 'Volume'.")
    p.add_argument('lw_files', nargs='+', type=str, help="Labware definition files in the same order as on the bed (starting from slot 1)")
    p.add_argument('-o', '--outfile', type=str, default='output.py', help="The name of the output script")
    p.add_argument('-v', '--volume', type=str, help="Volume to pipette from all wells if not specified in the spreadsheet")
    p.add_argument('-a', '--aspiration_height', type=str, help='How far from the bottom of the well (in mm) should the pipette go when aspirating?')
    p.add_argument('-n', '--protocol_name', type=str, help='Custom name for the protocol (defaults to script name)')
    p.add_argument('-u', '--user', type=str, help="Your name (defaults to guessing based on your computer's account name)")
    p.add_argument('-t', '--new_tip', default='always', action='store_const', const='never', help="If set, don't drop tips between pipetting (for testing with water)")
    return p
 
def main():
    p = parser()
    args = p.parse_args()
 
    if not args.outfile.endswith('.py'):
        args.outfile = args.outfile+'.py'
 
    if not args.protocol_name:
        args.protocol_name = 'Cherrypick from spreadsheet'
    
    if not args.user:
        args.user = ''

    if args.new_tip == 'never':
        print("WARNING: Tip flag set, all pipette tips will be reused")
 
    # Load the first sheet of the Excel file
    input_data = read_excel(args.instruction_spreadsheet)
 
    istrue = lambda s: s.lower() in ['true', '1', '1.0', 't', 'y', 'yes', 'yeah', 'yup', 'ja', 'richtig']
 
    # Mask out unwanted rows
    if 'mask' in input_data.keys():
        mask = [istrue(str(v)) for v in input_data['mask']]
        for k in input_data.keys():
            input_data[k] = [input_data[k][i] for i in range(len(mask)) if mask[i]]
 
    # Figure out how much to pipette from each well
    volcol = False
    if 'volume' in input_data.keys():
        input_data['volume'] = [float(v) for v in input_data['volume']]
        volcol = True
    if volcol and args.volume:
        raise(RuntimeError("Conflicting input!  Volume specified in both spreadsheet and command line"))
    elif volcol:
        pass
    elif args.volume:
        input_data['volume'] = [args.volume]*len(input_data['source slot'])
    else:
        raise(RuntimeError("No volume information provided!  Either add a volume column to the spreadsheet or specify -v <number> to pipette the same volume from each well"))
    
    # Get aspiration height (something is spelled wrong here)
    aspcol = False
    if 'aspiration height' in input_data.keys():
        input_data['aspiration height'] = [float(v) for v in input_data['aspiration height']]
        aspcol = True
    if aspcol and args.aspiration_height:
        raise(RuntimeError("Conflicting input!  Aspiration height specified in both spreadsheet and command line"))
    elif aspcol:
        pass
    elif args.aspiration_height:
        input_data['aspiration height'] = [args.aspiration_height]*len(input_data['source slot'])
    else:
        print("INFO: No aspiration height provided, defaulting to 1 mm")
        input_data['aspiration height'] = [1]*len(input_data['source slot'])
 
    # Make sure the number of labware files provided makes sense
    try:
        assert len(args.lw_files) == len(set(input_data['target slot']).union(set(input_data['source slot'])))
        slot_to_labware = {i : args.lw_files[i-1] for i in range(1, len(args.lw_files)+1)} #(slots are 1-indexed)
    except:
        raise RuntimeError(f"The number of labware files provided ({len(args.lw_files)}) as arguments must match the number of used slots ({len(set(input_data['target slot']))}) on the device!")

    # Map the labware files onto slots                        
    input_data['target labware'] = [get_lw_name(slot_to_labware[s]) for s in input_data['target slot']]
    input_data['source labware'] = [get_lw_name(slot_to_labware[s]) for s in input_data['source slot']]

    # Check for empty values after the mask
    to_check = ['source slot', 'source well', 'target slot', 'target well', 'volume']
    for k in to_check:
        if (None in input_data[k]):
            raise(RuntimeError(f"There is a blank cell in column {k} at row {input_data['row numbers'][input_data[k].index(None)]}"))
    
    # Check to make sure all volumes make sense
    if (any(v < 1 for v in input_data['volume']) or any(v > 300 for v in input_data['volume'])):
        bad_wells = [str(r) for r, v in zip(input_data['row numbers'], input_data['volume']) if v < 1 or v > 300]
        raise(RuntimeError(f"Volumes must be between 1 and 300 µl for a P20+P300 pipette combo. Rows {', '.join(bad_wells)} outside range."))
    
    # Map the maximum fill volume of each target well into input_data
    target_well_names = [str(ts)+tw for (ts, tw) in zip(input_data['target slot'], input_data['target well'])]
    fill_volumes = {}
    for ss in set(input_data['target slot']):
        row_ids = [i for i, ts in enumerate(input_data['target slot']) if ts == ss]
        wells = [input_data['target well'][i] for i in row_ids]
        labware = slot_to_labware[ss]
        max_fills = get_well_volumes(labware, wells)
        for well, mf in zip(wells, max_fills):
            fill_volumes[str(ss)+well] = mf

    # Check to make sure that no wells will be overfilled by an instruction
    for rn, ts, tw, v in zip(input_data['row numbers'], input_data['target slot'], input_data['target well'], input_data['volume']):
        fill_volumes[str(ts)+tw] -= v
        if fill_volumes[str(ts)+tw] < 0:
            raise(RuntimeError(f"Well {tw} in slot {str(ts)} will be overfilled by {abs(fill_volumes[str(ts)+tw])} µl by instruction in row {rn}"))

    # Generate run script
    outfile = shutil.copy(os.path.join(get_script_path(), 'cherrypick_template.py'), args.outfile)
    with open(outfile, 'a') as f:
        # Write the instruction json function
        f.write("def myjson():\n")
        f.write("\treturn('''{\n")
        f.write(f'"new_tip":"{args.new_tip}",\\\n')
        f.write(f'"transfer_csv":"Source Labware,Source Slot,Source Well,Source Aspiration Height Above Bottom (in mm),Dest Labware,Dest Slot,Dest Well,Volume (in ul)\\\\n\\\n')
        for slw, ss, sw, sah, tlw, ts, tw, v in zip(
            input_data['source labware'], 
            input_data['source slot'], 
            input_data['source well'], 
            input_data['aspiration height'], 
            input_data['target labware'], 
            input_data['target slot'], 
            input_data['target well'], 
            input_data['volume']):
            f.write(f'{slw},{str(ss)},{sw},{str(sah)},{tlw},{str(ts)},{tw},{v}\\\\n\\\n')
        f.write("\"}''')\n")
 
        # Write protocol metadata
        f.write(create_metadata(args.protocol_name, sys.argv[0], args.user)+'\n')

    print(f"INFO: Wrote Opentrons run script to {outfile}")
    print("NOTE: Tipracks for the left pipette must be in even-numbered slots, right pipette in odd-numbered slots")
 
if __name__ == '__main__':
    main()