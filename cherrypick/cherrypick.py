# Cherrypicking script from Opentrons.  You can get this by filling out the form at https://protocols.opentrons.com/protocol/cherrypicking
# This script uses a p300 in the left mount with standard tips and a p20 in the right mount also with standard tips.
# Cherrypicking instructions are in the "transfer_csv" section of the _all_values parse
# Yes, everything needs to be in a single Python script.

PIP_LEFT = "p300_single_gen2"
PIP_RIGHT = "p20_single_gen2"
TIP_TYPE = "standard"
FLOW_RATE_ASPIRATE = 1400
FLOW_RATE_DISPENSE = 1400

def get_values(*names):
    import json
    _all_values = json.loads(myjson())
    return [_all_values[n] for n in names]

def run(ctx):
    new_tip, transfer_csv = get_values("new_tip", "transfer_csv")

    tiprack_map = {
        'p10_single': {
            'standard': 'opentrons_96_tiprack_10ul',
            'filter': 'opentrons_96_filtertiprack_20ul'
        },
        'p50_single': {
            'standard': 'opentrons_96_tiprack_300ul',
            'filter': 'opentrons_96_filtertiprack_200ul'
        },
        'p300_single': {
            'standard': 'opentrons_96_tiprack_300ul',
            'filter': 'opentrons_96_filtertiprack_200ul'
        },
        'p1000_single': {
            'standard': 'opentrons_96_tiprack_1000ul',
            'filter': 'opentrons_96_filtertiprack_1000ul'
        },
        'p20_single_gen2': {
            'standard': 'opentrons_96_tiprack_20ul',
            'filter': 'opentrons_96_filtertiprack_20ul'
        },
        'p300_single_gen2': {
            'standard': 'opentrons_96_tiprack_300ul',
            'filter': 'opentrons_96_filtertiprack_200ul'
        },
        'p1000_single_gen2': {
            'standard': 'opentrons_96_tiprack_1000ul',
            'filter': 'opentrons_96_filtertiprack_1000ul'
        }
    }

    pip_vol_map = {
        'p300_single_gen2' : {
            'min' : 19.9,
            'max' : 300
        },
        'p20_single_gen2' : {
            'min' : 1,
            'max' : 20.1
        }
    }

    # load labware
    transfer_info = [[val.strip().lower() for val in line.split(',')]
                     for line in transfer_csv.splitlines()
                     if line.split(',')[0].strip()][1:]
    for line in transfer_info:
        s_lw, s_slot, d_lw, d_slot = line[:2] + line[4:6]
        for slot, lw in zip([s_slot, d_slot], [s_lw, d_lw]):
            if not int(slot) in ctx.loaded_labwares:
                ctx.load_labware(lw.lower(), slot)

    # load tipracks in remaining slots
    # Tips for the left pipette are in even-numbered slots, right pipette in odd-numbered slots
    tiprack_left = tiprack_map[PIP_LEFT][TIP_TYPE]
    tiprack_right = tiprack_map[PIP_RIGHT][TIP_TYPE]
    left_racks = []
    right_racks = []
    for slot in range(1, 12):
        if slot not in ctx.loaded_labwares:
            if slot % 2 == 0:
                left_racks.append(ctx.load_labware(tiprack_left, str(slot)))
            else:
                right_racks.append(ctx.load_labware(tiprack_right, str(slot)))

    # load pipette
    pip_left = ctx.load_instrument(PIP_LEFT, 'left', tip_racks=left_racks)
    pip_right = ctx.load_instrument(PIP_RIGHT, 'right', tip_racks=right_racks)
    pip_left.flow_rate.aspirate = FLOW_RATE_ASPIRATE
    pip_left.flow_rate.dispense = FLOW_RATE_DISPENSE
    pip_right.flow_rate.aspirate = FLOW_RATE_ASPIRATE
    pip_right.flow_rate.dispense = FLOW_RATE_DISPENSE

    def parse_well(well):
        letter = well[0]
        number = well[1:]
        return letter.upper() + str(int(number))

    if new_tip == 'never':
        pip_left.pick_up_tip()
        pip_right.pick_up_tip()
    for line in transfer_info:
        _, s_slot, s_well, h, _, d_slot, d_well, vol = line[:8]
        source = ctx.loaded_labwares[
            int(s_slot)].wells_by_name()[parse_well(s_well)].bottom(float(h))
        dest = ctx.loaded_labwares[
            int(d_slot)].wells_by_name()[parse_well(d_well)]
        vol = float(vol)
        if vol > pip_vol_map[PIP_LEFT]['min'] and vol < pip_vol_map[PIP_LEFT]['max']:
            pip = pip_left
        elif vol > pip_vol_map[PIP_RIGHT]['min'] and vol < pip_vol_map[PIP_RIGHT]['max']:
            pip = pip_right
        else:
            raise(RuntimeError(f"Volume {str(vol)} outside range of both pipettes"))
        pip.transfer(vol, source, dest, new_tip=new_tip)

    # Cleanup        
    if pip_left.has_tip:
        pip_left.drop_tip()
    if pip_right.has_tip:
        pip_right.drop_tip()

