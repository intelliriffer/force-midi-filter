#!/bin/sh
############################################################
# Copy this File to $mmPath/AddOns to Launch Automatically
###########################################################

# Set up the environment
mmPath=$(cat /dev/shm/.mmPath)
. $mmPath/MockbaMod/env.sh

if test "$1" == "kill"; then
	#kill all midifilter processes
	for pid in $(pgrep -f midifilter.py); do kill -9 $pid; done

else
	python3 $mmPath/AddOns/force-midi-filter/midifilter.py 2>/dev/null &
fi
