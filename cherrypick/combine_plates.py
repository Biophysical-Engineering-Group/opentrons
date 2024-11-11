import argparse
import shutil
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) # sorry, this is dumb but I didn't want to force you to install this as a package.
from ot_lib import get_lw_name, get_script_path, create_metadata # You need the above line to be able to import from the parent directory without installing it as a package

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument('source_lw', type=str, help="Source labware definition file")
    p.add_argument('source_slot', type=str, help="Source slot on the Opentron")
    p.add_argument('dest_lw', type=str, help="Destination labware definition file")
    p.add_argument('dest_slot', type=str, help="Destination slot on the Opentron")
    p.add_argument('volume', type=float, help="Maximum volume to move")
    p.add_argument('outfile', type=str, help="The name of the output script")
    p.add_argument('-n', '--protocol_name', type=str, help='Custom name for the protocol (defaults to script name)')
    p.add_argument('-u', '--user', type=str, help="Your name (defaults to guessing based on your computer's account name)")
    return p


def main():
    p = parser()
    args = p.parse_args()

    if not args.outfile.endswith('.py'):
        args.outfile = args.outfile+'.py'

    if not args.protocol_name:
        args.protocol_name = 'combine_plates'
    
    if not args.user:
        args.user = ''

    source_lw = get_lw_name(args.source_lw)
    dest_lw = get_lw_name(args.dest_lw)

    rows = list(map(chr,range(ord('A'),ord('H')+1)))
    cols = list(range(1, 13))

    outfile = shutil.copy(os.path.join(get_script_path(), 'cherrypick.py'), args.outfile)

    with open(outfile, 'a') as f:
        f.write("'''\"")
        f.write("Source Labware,Source Slot,Source Well,Source Aspiration Height Above Bottom (in mm),Dest Labware,Dest Slot,Dest Well,Volume (in ul)\\\\n\\\n")
        for r in rows:
            for c in cols:
                # This just moves the liquid in each input to the output.
                f.write(f"{source_lw},{args.source_slot},{r}{c},1,{dest_lw},{args.dest_slot},{r}{c},{args.volume}\\\\n\\\n")
        f.write("\"''')\n")

        # Write protocol metadata
        f.write(create_metadata(args.protocol_name, sys.argv[0], args.user)+'\n')

if __name__ == '__main__':
    main()