#!/bin/sh

appname=forceMidiFilter
appTitle=FORCE-MIDI-FILTER
appDir=force-midi-filter

################ NO NEED TO EDIT BELOW THIS LINE ###############

mmPath=$(cat /dev/shm/.mmPath)
. $mmPath/MockbaMod/env.sh

runDir="$mmPath/AddOns/"
installroot="$mmPath/AddOns/$appDir/"
runScript="$runDir/run_$appname.sh"
execDir="$mmPath/AddOns/$appDir/node/bin"

mode=$1

echo "
***********************************************************
*   $appTitle  AddOn Manager for Mockba Mod Force 3.5 and Above      *
***********************************************************
"

if [ "$mode" == "DISABLE" ]; then

	for pid in $(pgrep -f midifilter.py); do kill -9 $pid; done

	rm -f "$runScript"

	echo "$appTitle has been disabled from Auto Launch"
fi

if [ "$mode" == "UNINSTALL" ]; then

	echo "UNINSTALL NOT REQUIRED.. Disabling Instead!"
	DISABLE
fi

if [ "$mode" == "ENABLE" ]; then
	cp -f "$installroot/run_$appname.sh" "$runScript"
	echo "$appTitle has been enabled for Auto Launch"
	echo "Restart Force Process (New Project and it should show up)"

fi
