#!/bin/bash
#This is an example of a shell script that allows one to run compengine scripts 
#from cron.
#important concepts:
#  1. Setting environment variables, cron usually has a limited environment.
#  2. Looping thru a station list to modify a compengine algoritm
#  3. Piping CompEngine script to the interpreter
#
#===============================================================================
#Set Environment variables and change to appropriate directory
#===============================================================================
export LD_LIBRARY_PATH=/usr/cwms/java/jre/lib/sparc:/usr/cwms/lib:/usr/local/lib:/usr/openwin/lib:/usr/lib:/oraclebase/product/11.1_client/lib32:/oraclebase/product/11.1_client/lib32:/usr/local/lib:/usr/local/ssl/lib

SOURCE=/usr2/rwcds/ce/v1
OFFICE=nww
CE=wq
SCRIPT_NAME=cequal.sh
CE_SOURCE=$SOURCE/$OFFICE/$CE
cd $CE_SOURCE

FINISH=`date -u +%y%m%d%H%M%S`

#===============================================================================
# Set lookback time
#===============================================================================

lkbck="5d"

#===============================================================================
#Loop thru stationlist, assign variables and pipe script to compengine
#The example script:
# matches the time offset to an existing path
# stores a path in a timeseries variable called TEMP
# calculates the daily max, min and average water temperature for the path
# stores results to the database  
#===============================================================================

for LOC in `cat cequal_temps.stationlist`
do
if [ "$LOC" == "ORFI" ]
then
  echo $LOC
  INTERVAL="15Minutes"
else
  INTERVAL="1Hour"
fi
echo "computing $LOC"
# Run CompEngine
$SOURCE/common/bin/compengine << !
#---Begin compengine script
set lookback $lkbck
matchoffset DWR.Flow-Out.Ave.~1Day.1Day.CBT-REV
def TEMP $LOC.Temp-Water.Inst.$INTERVAL.0.GOES-RAW 
store max 1d TEMP $LOC.Temp-Water.Max.~1Day.1Day.GOES-COMPUTED-REV
store min 1d TEMP $LOC.Temp-Water.Min.~1Day.1Day.GOES-COMPUTED-REV
store average 1d TEMP $LOC.Temp-Water.Ave.~1Day.1Day.GOES-COMPUTED-REV
exit
#----
!
done
#===============================================================================
#Echo stats 
#===============================================================================

FINISH=`date -u +%y%m%d%H%M%S`
ELAPSED=`expr $FINISH - $START`
echo " --- Finished at $FINISH UTC in $ELAPSED seconds"
