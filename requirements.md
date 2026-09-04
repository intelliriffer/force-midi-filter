# Project Requirements
Create a python script for filtering incoming midi input. (primarily for moddeed AKAI Force and Mac)

## It should
1. **Listing mode:** Take -l (-list) as input parameter and list available midi input ports and exit.
2. Normal Mode: it should read a config file in the same directory.as the python scrpipt. The config file should have midi port name s well as some sort of schema about what to filter and what not. ou decide best scheme that is easier for non programmers to write and edit.
3. It should create ab output port MidiFilter-Mockba to which it passes filtered midi input to.
4. The user should be able to filter all messags on a channel or just specific messages on a channel,
   perhaps we could have lines such as:
   CH-1= BLOCK (filters everytihg i.e. blocks all messaes from this channel)
   CH-1= CC,PC,NOTE,AFTERTOUCH,PRESSURE,PITCHBEND These Nessage types will not be filterd and should go to midi output.
   CH-2=CC,PC  ONly incoming  CC and PC events on channel are passed to output, all other messages are filterd oput..
5. Any channel not spcified in the file should be considered totally BLOCKED (filterd).
6. It should Ignore All likes that are not MIDIPORT=[wildcard] or CH-[0-16]
7. Any comments (lines with # or text in line after # should be considered comment and not read.
 
### The input MidiPort
1.The Midiport in the file should be treated a wild card and should be matched againt the midi ports devices present and any matching ports should be opened and listened to for midi input. for example if config has  launchpad as midi port it should match all ports that have "launchpad" in it and open them.
2. If the MidiPort is not defined in config it should throw and error and exit.
3. If a midi port is mentiond , but n matches  are  found, it should wait and keep polling until the port is availalbe and open 


## Tech Stack
1. Compatible with python 3.8
2. Use Midi for midi
3. Should not use any third party libraries. (minimal and native )


### Deliverables
- **midifilter.py** The Python Script.
- **config.txt** The Config File (include config file useage as comments the file as well as all the message types (CC,PC etc)
- **test.py** a python script to test al; functions and config loading properly. 
- README.md A Basic Text file for the Git Repo describing the project etc and linking to requirements.md
