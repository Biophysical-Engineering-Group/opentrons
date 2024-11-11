# Cherrypicking

The art of taking liquid from a list of specific wells and depositing them in other specific wells.

## Scripts

### cherrypick
Slightly modified cherrypicking script from the [Opentrons repository](https://protocols.opentrons.com/protocol/cherrypicking).  Modified by the other scripts here to generate experiment-speicific machine instructions.


### combine_plates
Pipette every well from one 96-well plate into the same position in another plate.  For combining DNA plates.
```
python combine_plates.py ../labware/abgeneidt_96_wellplate_1.2ul.json 1 ../labware/abgeneidt_96_wellplate_1.2ul.json 2 100 ../runs/example_combine.py
```

### pool_from_sheet
Given a plate definition Excel or csv file with additional `Mask`, `Target` and `Volume` columns, pipette `Volume` liquid from wells where `Mask` == 1 into well `Target` in the destination plate.
```
python pool_from_sheet.py pool_example.xls ../labware/abgeneidt_96_wellplate_1.2ul.json 1 ../labware/pcr_48_8strip.json 2 ../runs/example_pool.py
```
