Compengine Changelog
====================

Compengine 2.0 (1 February 2014)
----------------------------------
* added string utilities ()
* added gage correction function
* added noaa_relative_humidity computation
* added init_ts function to initialize timeseries

Compengine 1.5 (1 July 2013)
--------------
* added filtering routines (filter)
* added outlier removal (rmoutliers)
* added value culling routines (cull above|below|equal)


Compengine 1.4 (1 May 2013)
-----------------------------
* you can now load lists from the file system:
`loadlist <FILENAME>`
    
    def STALIST loadlist cequal_temps.list

* added list functions:
    * add to the end of a list:
    
        push <LIST> <TIMESERIES or variable>

    * get and remove a variable from the list:
            
        pop <LIST>

* you can now loop each item in the list:
    for <VARIABLE> in <LIST> do
      <COMMAND 1>
      ..
      <COMMAND N>
    end
    
###example using new features:
        set prompt off
        #Load list from filesystem
        def TEMPS loadlist temperature.list
        #Add station to list
        push TEMPS string BIGI
        #Loop thru list create pathname and print it out
        for STA in TEMPS do
          def PATH stringcat STA .Temp-Air.Inst.1Hour.0.RFC-RAW
          print PATH
        end

results of above code:

    ANQW.Temp-Air.Inst.1Hour.0.RFC-RAW
    ORFI.Temp-Air.Inst.1Hour.0.RFC-RAW
    DWR.Temp-Air.Inst.1Hour.0.RFC-RAW
    ALW.Temp-Air.Inst.1Hour.0.RFC-RAW
    BIGI.Temp-Air.Inst.1Hour.0.RFC-RAW

Compengine 1.3.5 (15 September 2012)
--------------------------------------
added a center moving average routine:
        
    centermovingaverage 1h <TIMESERIES>
 --or--
    
    cma 1h <TIMESERIES>


Compengine 1.3.3 (15 August 2012)
-----------------------------------
*Added the following string utilities:
    * stringreplace
    * stringcat

* exposed the prompt variable:
`set prompt off` now turns off the prompt, which is useful for automated batch jobs

* Compengine is now shebangable
