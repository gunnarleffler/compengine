#Compengine

###A timeseries computation engine for use with CWMS 2.1+ databases

####Version 2.0

####1 February 2014

Introduction
============
The .compengine. is intended to be a supplementary computation and
calculation engine for use with the US Army Corps of Engineers CWMS 2.0
database and greater. It has a simple, timeseries centric language that
abstracts all the looping and programmatic cruft involved with
timeseries computations. It allows the user to specify, chain and store
timeseries computations directly into the database. One also can store
intermittent computations as time series objects. Time series objects are
containers that contain an arbitrary amount of time series data which consist of:

**[timestamp, value, quality flag]**


The language can be used directly in an interpreter. Scripts can be
formed from commands and piped to the interpreter. The interpreter is
case sensitive. Compengine can be run in both windows and unix
environments. It requires Python 2.6+, oracle binaries and the python
cx\_Oracle package being installed. An example location for compengine
to be stored is as follows:


`/usr2/rwcds/ce/v1/common/bin`


The compengine can be run interactively from a shell prompt by executing
the compengine:


`$ ./compengine`


Compengine scripts are collections of commands written in the compengine
language. To execute batch scripts, simply pipe the contents to the
compengine:


 `cat inflow.ce | compengine`


One can also make standalone executable compengine scripts by adding a
shebang at the beginning of the script:

` \#!/usr/bin/env /usr/ce/common/bin/compengine`


Syntax
======

The interpreter is *case sensitive*. The basic syntax of this engine
follows the following rules:

`command <parameters (optional)> <source TS> <destination TS
(optional)>`


Text following the hash symbol '\#' is treated as comments by the
interpreter.


Commands
========

##accumulate

---
The *accumulate* command sums up all values on an interval returns a
timeseries with accumulated values for each time interval.

#### Usage:

`accumulate <timeinterval> <timeseries>`

#### Examples:

The following example is accumulates 7 days worth of 6 hour incremental
precip data to daily incremental precip data:

    set lookback 7d
    print accumulate 1d 75S.Precip-Inc.Total.6Hours.6Hours.RFC-RAW

##add

---
The *add* command can add two timeseries together, or add a constant to
a timeseries. The operands are communitive.

#### Usage:

`add <timeries1|constant1> <timeseries2|constant2>`

#### Examples:

The following example is equivalent to TS1 = TS2 + TS3:

    def TS1 add TS2 TS3

The following example is equivalent to TS1 = TS2 + 3:
    
    def TS1 add TS2 3

##average
The *average* command steps through the specified timeseries, aggregates
values according to the specified time interval and returns a timeseries
with the average (mean) for each time interval.

#### Usage:

`average <time interval> <timeseries>`

#### Examples:

The following example averages a timeseries from the database and stores
it in the variable AVG.
    
    def AVG average 1d ARWO.Flow.Inst.0.0.MIXED-COMPUTED-REV

##bye

---
The *bye* command tells the interpreter to stop what it is doing and
exit back to the operating system. This command must be located at the
end of all scripts. *See also exit*.

##def

---
The *def* (for define) command defines a time series variable. Time
series can be directly referenced in the database by specifying a path.

#### Usage:

`def <timeseries>`

#### Examples:

    def numerator DWQI.Pres-Water-TotalGas.Inst.15Minutes.0.GOES-REV
    def denominator DWQI.Pres-Air.Inst.15Minutes.0.GOES-REV

The results from computations can be stored in variables. The example
below stores the resultant time series from the percent command into a
variable called .TDG.:
    
    def TDG percent numerator denominator

##divide

---
The *divide* command can divide one time series into another, divide a
constant into a timeseries or divide a timeseries into a constant. The
command is aliased as *div.*

#### Usage:

`divide <timeries1|constant1> <timeseries2|contant2>`

#### Examples:

The following example is equivalent to TS1 = TS2 / TS3:
    
    def TS1 divide TS2 TS3

The following example is equivalent to TS1 = TS2 / 3:
    
    def TS1 divide TS2 3

The following example is equivalent to TS3 = 3 / TS2:
    
    def TS1 divide 3 TS2

##exit

---
The *exit* command tells the interpreter to stop what it is doing and
exit back to the operating system. This command must be located at the
end of all scripts.

##export

---
The *export* command writes a timeseries to the filesystem.

#### Usage:
`export <filename> <timeseries>`

#### Examples:
Data directly from the database can be exported to the filesystem:
    
    export foo.txt DWQI.Pres-Water.Inst.15Minutes.0.GOES-REV

Results from computations can be exported to the filesystem:
    def BAR average 6h DWQI.Pres-Water.Inst.15Minutes.0.GOES-REV
    export bar.txt BAR

##filter

---
The filter command filters choppy data using the Savitzky-Golay
Smoothing Filter.

*From http://en.wikipedia.org/wiki/Savitzky-Golay\_smoothing\_filter*

*The **Savitzky Golay smoothing filter** is a filter that essentially
performs a local polynomial regression (of degree k) on a series of
values (of at least k+1 points which are treated as being equally spaced
in the series) to determine the smoothed value for each point. The main
advantage of this approach is that it tends to preserve features of the
distribution such as relative maxima, minima and width, which are
usually 'flattened' by other adjacent averaging techniques (like moving
averages, for example)..*


The parameters used in the compengine function sgfilter() are:

1. window_size integer
2. filter_order  integer
3. derivative = 0  *<this is currently hard coded with 0\>*
4. time_series TimeSeries data


Where window_size, the quantity of data points to include in each
calculation, is an ODD positive integer value \>= filter\_order + 2


Where filter_order is the order of the polynomial used in the
filtering/fitting. Values of 2 and 4 seem to work best for noisy data or
data with extreme fluctuations. It is positive integer value \<
window_size -1


Where derivative is the order of the derivative to compute where *0=
smoothing only*. This is the default and only option currently. For a
detailed explanation of the filter please refer to:\

[http://www-inst.eecs.berkeley.edu/\~ee123/fa11/docs/SGFilter.pdf](http://www-inst.eecs.berkeley.edu/~ee123/fa11/docs/SGFilter.pdf)

Wikipedia has a good, brief explanation with graphics and an animation
for visualization here:

[http://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay\_smoothing\_filter](http://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_smoothing_filter)

#### Usage:

`Filter <windowsize> <filter order> <timeseries>`

#### Example:

    # Perform Savitsky-Golay smoothing and store to the database
    def SMOOTH_INFLOW filter 13 2 LOC.Flow-In.Inst.0.0.MIXED-RAW
    store SMOOTH_INFLOW LOC.Flow-In.Inst.0.0.MIXED-COMPUTED-REV

##gagecorrect

---
At times a sensor in the field is reading values incorrectly, and a correction is published.
The *gagecorrect* command looks up values from the specified timeseries and
rates them using the specified correction file. The command will look for 
correction files in the directory specified in the *rdbpath* internal variable. The 
gagecorrect command will correct any parameter, it's intended use is to correct raw stage
values. Correction files are expected to be in rdb format and have an extension
of `.corr.rdb`.

#### Usage:

`gagecorrect <rdbfile|detect> <timeseries>`

#### Examples:

The following example turns an elevation into storage.

    gagecorrect ANAW.corr.rdb ANAW.Stage.Inst.15Minutes.0.GOES-RAW


The following example corrects a stage value and attemts to detect which correction rdb 
to use. The results are stored in the "CORRECTED\_STAGE" variable and then stored to the
database:

    def CORRECTED_STAGE gagecorrect WYNW.rdb WYNW.Stage.Inst.15Minutes.0.GOES-RAW
    store CORRECTED_STAGE WYNW.Stage.Inst.15Minutes.0.GOES-REV

##hardsnap

---
The *hardsnap* command attempts to make a regular interval timeseries by
assigning values closest to each interval a new timestamp. It differs from 
the snap function in that it uses the beginning of the time window as the
first time in the snapped timeseries. As opposed to the plain snap function \(see snap\)
function which uses the first timestamp of the input as the beginning timestamp in the
resultant timeseries.  The time buffer parameter is the range around each snap time 
where the function attempts to find a value. It is defined by a timebuffer value.
If the "time buffer" is greater than interval/2 results can become inconsistent.
In the case that a supplied time buffer is greater than interval/2, the computation
yields a warning and truncates the timebuffer to half of the supplied interval.

#### Usage:

`hardsnap <interval> <time buffer> <timeseries>`

#### Examples:

The following example snaps an irregular path in the database to a
timeseries with a 1h interval with a resulting start time of 8h after midnight.
The search buffer around each interval is +- 30 minutes.

    set offset 8h
    snap 1h 30m ACRW.Stage.Inst.0.0.RFC-RAW

##init_ts

---
The *init_ts* command makes a regular interval timeseries populated with a specified value.
The extents of the timseries are bounded by the current settings for "starttime" and "endtime"

#### Usage:

`init_ts <interval> <value>`

#### Examples:

The following example creates an hourly timeseries with populated with 0 values.
    
    def BLANK init_ts 1h 0.0


##inflow

---
The *inflow* command calculates inflow from a given storage and outflow
using the following formula:

**Qin =Delta S + Qout**

It expects the units for outflow input values to be in CFS and the units
for storage input values to be in Acre-Feet. It converts Changein storage
to volume by looking at the time interval between each timestep.

#### Usage:

`inflow <storage timeseries> <outflow timeseries>`

#### Examples:

The following example compute inflow and store it in the variable *QIN*.
     
    def QIN inflow STOR DWR.Flow-Out.Ave.1Hour.1Hour.CBT-RAW

##interpolate

---
The *interpolate* command linearly interpolates the specified timeseries
on the specified interval.

#### Usage:

`interpolate <interval> <timeseries>`

#### Examples:

The following example will interpolate a 6hour forecast into timeseries
variable called ALBO_1h with 1hour timesteps.


`def ALBO_1h interpolate 1h ALBO.Flow.Inst.6Hours.0.RFC-FCST`


##matchoffset

---
Lookback windows are calculated from the current time. This can cause
offset inconsistencies if calculations are done on data with intervals
greater than one hour. The **matchoffset** command will match hours and
minutes of the lookback window to ensure that the time offsets are the
same as the target timeseries . All computations will use this offset
until either the lookback window is changed or the matchoffset command
is run again.

#### Usage:

`matchoffset <timeseries>`

#### Examples:

The following example will match the offset to the specified \~1Day path
in the database:
    
    matchoffset DWR.Flow-In.Ave.~1Day.1Day.CBT-RAW


The following example will match the offset to the specified timeseries
container:
    
    matchoffset DAILY_INFLOW


##maximum (max)

---
The *max* command outputs the maximum value from the specified
timeseries on the specified interval

#### Usage:

`max <interval> <timeseries>`

#### Examples:

The following example will find the daily maximum of the specified path:

    max 1d ABEI.Temp-Air.Inst.0.0.USBR-RAW


##minimum (min)

---
The *min* command outputs the minimum value from the specified
timeseries on the specified interval

#### Usage:

`min <interval> <timeseries>`

#### Examples:

The following example will find the daily minimum of the specified path:
    
    min 1d ABEI.Temp-Air.Inst.0.0.USBR-RAW

##multiply

---
The *multiply* command can multiply two timeseries, or multiply a
constant and a timeseries. The operands are communitive.

#### Usage:

`multiply <timeries1|constant1> <timeseries2|constant2>`

#### Examples:

The following example is equivalent to TS1 = TS2 \* TS3:

    def TS1 multiply TS2 TS3

The following example is equivalent to TS1 = TS2 \* 3:

    def TS1 multiply TS2 3

##percent

---
The *percent* command calculates a percentage for every matching
timeseries stamp in the two timeseries specified.

#### Usage:

`percent <numerator> <denominator>`

#### Examples:

The following example will calculate Percent TDG from two timeseries in
the database and store it in a variable called TDG.

    def TDG percent PEKI.Pres-Water-TotalGas.Inst.1hour.0.GOES-REV
    PEKI.Pres-Air.Inst.1hour.0.GOES-REV

##print

---
The *print* command writes the string representation of timeseries
objects or internal variables to standard out. This can be used to
inspect timeseries while using the computation engine console or log
results while running batch jobs on a schedule (such as cron). *See
also string.*

#### Usage:

`print <timeseries|internal|string>`

#### Examples:

The following example sets a lookback period and prints the contents of
the timeseries within the lookback specified:

    set lookback 4d
    print DWR.Flow-In.Ave.~1Day.1Day.CBT-RAW

Example of output:

    18-May-2012 0700 22400.00 0.00
    19-May-2012 0700 20400.00 0.00
    20-May-2012 0700 18200.00 0.00
    21-May-2012 0700 16900.00 0.00



When a time series is printed, it consists of 3 columns. In order the
columns represent: 1) timestamps, 2) values and 3) qualities.

##set

---
The *set* command allows the user to change internal variables. Internal
variables influence the computations performed on timeseries, but are
not timeseries themselves. Examples of internal variables are the
lookback and lookforward windows. Time windows can be specified using a
notation that describes days, hours and minutes of granularity.
Examples:

    set lookback 7d10h5m
    set lookforward 10d



##store

---
The *store* command writes a timeseries to the database to the specified
path. The destination path is treated as a string literal. If a
destination path does not exist in the database, it will be created. It
returns a timeseries containter with the contents of what is stored to
the database.



#### Usage:

`store <source timeseries> <destination path>`


#### Examples:

The timeseries can be a time series variable. The following example
stores the contents in SMOOTH\_INF to the database.
    
    store SMOOTH_INF DWR.Flow-In.Ave.1Hour.1Hour.CBT-COMPUTED-RAW


The timeseries can the result of a computation. The following example
stores the 1day average of SMOOTH_INF to the database.

    store average 1d SMOOTH\_INF
    DWR.Flow-In.Ave.~1Day.1Day.CBT-COMPUTED-RAW


##subtract

---
The *subtract* command can subtract one time series from another,
subtract a constant from a timeseries or subtract a timeseries from a
constant. The command is aliased as *sub.*

#### Usage:

`subtract <timeries1|constant1> <timeseries2|contant2>`

#### Examples:

The following example is equivalent to TS1 = TS2 - TS3:
    
    def TS1 subtract TS2 TS3


The following example is equivalent to TS1 = TS2 - 3:
    
    def TS1 subtract TS2 3


The following example is equivalent to TS1 = 3 - TS2:
    
    def TS1 subtract 3 TS2

##rate

---
The *rate* command looks up values from the specified timeseries and
rates them using the specified rdb file. The command will look for rdb
files in the directory specified in the *rdbpath* internal variable. The
rate command will rate any parameter.

#### Usage:

`rate <rdbfile> <timeseries>`

#### Examples:

The following example turns an elevation into storage.
    
    rate DWR.rdb DWR.Elev-Forebay.Inst.1Hour.0.CBT-RAW


The following example converts a stage to flow and stores it in a
variable called WYNW\_FLOW:
    
    def WYNW\_FLOW rate WYNW.rdb WYNW.Stage.Inst.15Minutes.0.GOES-RAW

##rate2

---
The *rate2* command differs from the rate command in that it switches
the dependent and independent variables. It looks up values from the
specified timeseries and rates them using the specified rdb file. The
command will look for rdb files in the directory specified in the
*rdbpath* internal variable. The rate command will rate any parameter.

#### Usage:

`rate2 <rdbfile> <timeseries>`

#### Examples:

The following example turns storage into elevation.
    
    rate2 DWR.rdb DWR.Storage.Inst.1Hour.0.CBT-RAW


The following example converts a flow to a stage and stores it in a
variable called WYNW\_STAGE:
    
    def WYNW_STAGE rate WYNW.rdb WYNW.Flow.Inst.15Minutes.0.GOES-RAW


##rollingaverage

---
The *rollingaverage* command calculates a simple moving average for the
previous n datapoints in the specified time interval. The timestamp for
the first datapoint returned will be Tstart+Tinterval.


#### Usage:

`rollingaverage <timeinterval> <timeseries>`


#### Examples:

The following example returns the rolling average (simple moving
average) over 6 hours for values stored in the variable *INF*.
    
    rollingaverage 6h INF

##snap

---
The *snap* command attempts to make a regular interval timeseries by
assigning values closest to each interval a new timestamp. The
searchspace is defined by a timebuffer value. If the timebuffer is
greater than interval/2 results can become inconsistent. The computation
yield a warning if the timebuffer is greater than half of the interval.

#### Usage:

`snap <interval> <time buffer> <timeseries>`

#### Examples:

The following example snaps an irregular path in the database to a
timeseries with a 1h interval. The search buffer around each interval is
+- 30 minutes.
    
    snap 1h 30m ACRW.Stage.Inst.0.0.RFC-RAW

##string

---
The *string* command converts all characters following the command into
a string.

#### Usage:

`string <string literal>`

#### Examples:

The following example writes a string literal to standard out:
    
    print string Averaged hourly computed inflow


Example of output:

    Averaged hourly computed inflow



##tablelookup

---
The *tablelookup* command looks up values in a table using two specified
timeseries and rates them by bilinearly interpolating nearby values
using the specified table.. The command will look for table files in
the directory specified in the *rdbpath* internal variable. Table files
can be either comma delimeted or tab delimited. This command is aliased
as *bicurve.*

#### Usage:

`tablelookup <tablefile> <timeseries1> <timeseries2>`

#### Examples:

The following example turns a forebay elevation into storage.
    
    tablelookup sta_gate.table GATE_OPENING FOREBAY_ELEVATION


##timeshift

---
The *timeshift* command shifts the timestamp of every entry in a
timeseries by the specified time period. This can be used for lagging
flows to compute virtual gages among other things. NOTE: you can use
negative time periods if needed.

#### Usage:

`timeshift <time period> <timeseries>`

#### Examples:

The following shifts data stored in a path 6 hours into the future.
    
    def VIRT timeshift 6h ACRW.Stage.Inst.0.0.RFC-RAW


Example Programs
================
##Hello World

---
    print string HELLO WORLD!
    exit

##Rating storage-elevation, computing smoothed inflow

---
    #!/usr/bin/env /usr/ce/common/bin/compengine
    set lookback 1d
    matchoffset DWR.Flow-In.Ave.~1Day.1Day.CBT-RAW
    print string Averaged hourly computed inflow
    def STOR rate DWR.rdb DWR.Elev-Forebay.Inst.1Hour.0.CBT-RAW
    def INF inflow STOR DWR.Flow-Out.Ave.1Hour.1Hour.CBT-RAW
    def SMOOTH_INF rollingaverage 6h INF
    store SMOOTH_INF DWR.Flow-In.Ave.1Hour.1Hour.CBT-COMPUTED-RAW
    store average 1d INF DWR.Flow-In.Ave.~1Day.1Day.CBT-COMPUTED-RAW
    exit

##copying data by looping through a config file

---
    #!/usr/bin/env /usr/ce/common/bin/compengine
    set prompt off
    #
    # Assigning Rereg outflow to Project outflow 
    #
    set lookback 3h
    def STATIONS loadlist fcst.list
    #Loop through list of stations, split and 
    for S in STATIONS do
      def STAS stringsplit S
      def STA2 pop STAS
      def STA1 pop STAS
      print string =================================================
      print string ------- Assigning Rereg outflow to Project outflow -------
      def PATH1 stringreplace STA STA1 STA.Flow.Inst.~6Hours.0.RFC-FCST
      def PATH2 stringreplace STA STA2 STA.Flow-Out.Inst.~6Hours.0.RFC-FCST
      print PATH1
      print PATH2
      store @PATH1 PATH2
      print string -----------------------------------------------
    end
    
## Create a daily 30YR average

---
    #!/usr/bin/env /usr/ce/common/bin/compengine
    set prompt off
    #
    # Creates a Daily Average using 1980-2010 data
    #
    set starttime string oct 1, 1980
    set endtime string sep 30, 2010
    #setup
    push FNAMES string 81_10PST.list
    push OFFSETS string 8h
    #Loop through list of filenames and compute averages
    for FNAME in FNAMES do
      set offset pop OFFSETS
      print string =================================================
      print offset
      #Load list of stations and parameters from filesystem
      def PATHLIST loadlist FNAME
      for PATH in PATHLIST do
        #Format output path
        def PATH2 stringreplace -FCST -30YEAR2010-COMPUTED-FCST PATH
        def PATH2 stringreplace -RAW -REV PATH2
        def PATH2 stringreplace -COMPUTED-REV -REV PATH2
        def PATH2 stringreplace -REV -30YEAR2010-COMPUTED-REV PATH2
        def PATH2 setpart C PATH2 Ave
        def PATH2 setpart D PATH2 ~1Day
        def PATH2 setpart E PATH2 1Day
        #print out what we are working on for logging purposes
        print stringcat source: PATH
        print stringcat destination: PATH2
        def AVG averageWY hardsnap 1d 6h filter 13 2 @PATH
        store timeshift 1096d AVG PATH2
        print string -----------------------------------------------
      end
    end



