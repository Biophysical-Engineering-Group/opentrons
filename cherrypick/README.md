# Cherrypicking

The art of taking liquid from a list of specific wells and depositing them in other specific wells.

## Scripts

### cherrypick_template
Modified cherrypicking script from the [Opentrons repository](https://protocols.opentrons.com/protocol/cherrypicking).  Further modified by the other scripts here to generate experiment-speicific machine instructions.

### setup_cherrypick
Take a spreadsheet and the list of labware configuraiton files for each slot, modify cherrypick_template.py to run the provided spreadsheet.  Example of use:
```
python setup_cherrypick.py cherrypick_example.xlsx ../labware/corningidt_96_wellplate_500ul.json ../labware/abgeneidt_96_wellplate_1200ul.json ../labware/printed_24_tuberack_1500ul.json ../labware/pcr_48_8strip.json -o ../runs/my_cherrypick.py
```
**Required Parameters**  
* Instruction file : Excel of csv file where each line corresponds to an action.  An example can be found in cherrypick_example.xlsx.  Must have the following columns: source slot, source well, target slot, target well.  Optional columns: volume, aspiration height, mask  
* Labware files : The list of labware loaded in each slot of the Opentron. This might mean there are repeated entries.

**Optional Parameters**  
* -o : Ouput file name
* -v : Specify a single volume (in µl) for every transfer. Required if there is no volume column in the spreadsheet
* -a : Specify a single aspiration height (in mm) above bottom for each transfer.  Can also be set in the spreadsheet.  If not set, will default to 1 mm
* -n : The protocol name which will be displayed in the Opentrons app on the device computer.
* -u : Your name.  If not set, will be your account name on your computer
* -t : If set, don't drop tips between transfers.  Used for testing
