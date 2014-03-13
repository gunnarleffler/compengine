#!/usr/local/bin/python
#Computation Engine Library v1.3.1
#15 Sep 2012
#Author: Gunnar Leffler
#      : Mike Stanfill

import sys,os,time,datetime
import cx_Oracle
from math import factorial
import numpy as np


class timeSeries:
  #"overloaded" timeSeries constructor
  def __init__ (self, data = None):
    self.status = "OK"
    #Data is a nested list with the following structure [datetime,float value, float quality]
    self.data = []
    if data != None:
      #set internal data member to data and filter out blanks
      for line in data:
        if line != []:
          if line[1] != None: 
            self.data.append(line)
  
  #Equivalent to toString()
  def __str__ (self):
    output = ""
    for line in self.data:
      try:
        output += "%s\t%.2f\t%.2f\n" % (line[0].strftime("%d-%b-%Y %H%M"),line[1],line[2])
      except:
        output += "%s\t\t\n" % line[0].strftime("%d-%b-%Y %H%M")
    return output

  #gets status message of object and resets it to "OK"  
  def getStatus(self):
    s = self.status
    self.status = "OK"
    return s

  #returns a valuea at a given timestamp
  #returns None type if not found
  def findValue(self,timestamp):
    for line in self.data:
      if line[0] == timestamp:
        return line [1]
      elif line[0] > timestamp:
        return None
    return None

  #interpolate values
  def interpolateValue(self, x0, y0, x1, y1, x):
    m = (y1 - y0) / (x1 - x0)
    output = y0 + (x - x0) * m
    return output

  #interpolates timeseries based on a given interval of type timedelta 
  #returns a timeseries object
  def interpolate(self,interval):
    _data = []
    try:
      for i in xrange(0,len(self.data)-1):
        startTime = self.data[i][0]
        deltaT = (self.data[i+1][0] - startTime)
        steps = int(deltaT.total_seconds()/interval.total_seconds())
        quality = self.data[i][2]
        for j in xrange(0,steps):
          value = self.interpolateValue(0,self.data[i][1],deltaT.total_seconds(),self.data[i+1][1],j*interval.total_seconds())
          _data.append([startTime+(interval*j),value,quality])
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)

  #averages timeseries based on a given interval of type timedelta 
  #returns a timeseries object
  def average(self,interval):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      i = 0
      count = len(self.data)     
      endTime = self.data[i][0]
      while i < count:
        startTime = endTime 
        endTime = startTime + interval
        quality = self.data[i][2]
        n = 0
        sum = 0
        while self.data[i][0] < endTime:
          sum += self.data[i][1]
          n += 1
          i += 1
          if i >= count:
            break
        if n != 0:
          _data.append([endTime,sum/n,quality])
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)

  #averages each element in the timeseries in previous water years
  #returns a timeseries object
  def averageWY(self):
    def toWY(t):
      output = t.year
      if t.month > 9: output += 1
      return output

    def fromWY(year,month):
      output = year
      if month > 9: output -= 1
      return output

    def inWY(WY,t):
      if t.month < 10 and WY == t.year:
        return True
      if t.month > 9 and WY == (t.year +1):
        return True
      return False
    
    def toDict(data): #Turns timeseries into a dictionary for efficiency purposes
      output = {}
      for i in xrange(len(self.data)):
        output[self.data[i][0]]=i  
      return output

    _data = []
    if self.data == []:
      return timeSeries()
    dd = toDict(self.data)
    try:
      i = 0
      startWY= toWY(self.data[0][0])
      endWY = toWY(self.data[-1][0])
      count = len(self.data)
      #advance to the latest WY      
      while i < count and not inWY(endWY,self.data[i][0]): i+= 1
      #average current timeslice
      while i < count:
        sum = 0
        t = self.data[i][0]
        n = 0
        for WY in xrange(startWY,endWY+1):
          try:
            t2 = datetime.datetime(year = fromWY(WY,t.month),month=t.month,day=t.day,hour=t.hour,minute=t.minute)
            if t2 in dd:
              val = self.data[dd[t2]][1]
              n+=1
              sum += val
          except:
            pass
        quality = self.data[i][2]
        if n != 0:
          _data.append([t,sum/n,quality])
        i+=1
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)

  #accumulates timeseries based on a given interval of type timedelta 
  #returns a timeseries object
  def accumulate(self,interval):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      i = 0
      count = len(self.data)     
      endTime = self.data[i][0]
      while i < count:
        startTime = endTime 
        endTime = startTime + interval
        quality = self.data[i][2]
        n = 0
        sum = 0
        while self.data[i][0] < endTime:
          sum += self.data[i][1]
          n += 1
          i += 1
          if i >= count:
            break
        if n != 0:
          _data.append([endTime,sum,quality])
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)

  #returns a max or a min based for a given interval
  #basse
  #returns a timeseries object
  def maxmin(self,interval,cmp):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      i = 0
      count = len(self.data)     
      endTime = self.data[i][0]
      while i < count:
        startTime = endTime 
        endTime = startTime + interval
        quality = self.data[i][2]
        probe = self.data[i][1]
        while self.data[i][0] < endTime:
          if cmp (self.data[i][1],probe):
            probe = self.data[i][1]
          i += 1
          if i >= count:
            break
        _data.append([endTime,probe,quality])
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)

  #========================================================================
  # Savitzky-Golay Smoothing filter using Numpy
  #========================================================================
  def savitzky_golay(self, window_size, order, deriv=0, rate=1):
    try:
      window_size = np.abs(np.int(window_size))
      order = np.abs(np.int(order))
    except ValueError:
      raise ValueError("SGFilter:window size and order must be of type int")

    if window_size % 2 != 1 or window_size < 1:
      raise TypeError("SGFilter:window size must be positive number")
    if window_size < order + 2:
      raise TypeError("SGFilter:window size is too small for the polynomials order")

    y = []

    #for x in xrange(0, len(self.data)-1):
    #  yy = self.data[x][1]
    #  print yy

#    for line in self.data:
#      if line[0] != None:
#        y.append(line[0][0])

    _data = self.data
    #.tolist()

    for x in xrange(0, len(_data)-1):
      yy = _data[x][1]
      y.append(yy)

    order_range = range(order+1)
    half_window = (window_size -1) // 2

    # precomute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)

    # pad the signal at the extremes with values taken from the signal itself
    #firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )

    firstvals = []
    v = y[0]

    for i in range(half_window):
      firstvals.append(v)


    #lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    lastvals = []
    v = (y[len(y)-1:])[0]

    for i in range(half_window):
      lastvals.append(v)

    y = np.concatenate((firstvals, y, lastvals))

    tsd = np.convolve( m[::-1], y, mode='same')
    # remove the appended/padded values at beginning/end of data
    tsd = tsd[(window_size-1)/2:len(tsd)-(window_size-1)/2]

    _data = []
    for x in range(0, len(self.data)-1):
      _data.append([self.data[x][0], tsd[x], 0])

    return timeSeries(_data)
  #========================================================================
  #========================================================================

  #========================================================================
  # Remove Outliers using Standard Deviation
  #========================================================================
  def remove_stddev_outliers(self, threshold=1.5):
    good = []
    _data = []
    a = []

    # get the slice of values from timeseries
    # y = np.array(self.data)
    # a = y[:,1]
    for rec in self.data:
      a.append(rec[1])

    avg = np.average(a)

    # pad the first element with average
    a = [avg] + a
    out = [None] * len(a)
    good.append(a[0])

    std = np.std(a)
    stdm = std * threshold

    for n in range(1, len(a) ):
      dev = abs(a[n] - good[-1])

      if dev < stdm:
        good.append(a[n])
        out[n]=a[n]
      else:
        out[n] = None

    # remove the first (avg) element
    out = out[1:]

    # replace the values, only non nulls
    # these will get interpolated later
    for x in range(0, len(self.data)):
      if out[x] != None:
        _data.append([self.data[x][0],out[x],self.data[x][2]])

    return timeSeries(_data)


  #averages timeseries based on a given interval of type timedelta 
  #returns a timeseries object
  def rollingaverage(self,interval):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      i = 0
      count = len(self.data)     
      while i < count:
        startTime = self.data[i][0]
        endTime = startTime + interval
        if endTime > self.data[-1][0]:
          break
        quality = self.data[i][2]
        n = 0
        sum = 0
        while self.data[i+n][0] <= endTime:
          sum += self.data[i+n][1]
          n += 1
          if i+n >= count:
            break
        if n != 0:
          _data.append([endTime,sum/n,quality])
        i+=1
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)


  #averages timeseries based on a given interval of type timedelta 
  #returns a timeseries object containing center moving average
  def centerMovingAverage(self,interval):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      i = 0
      interval = interval
      count = len(self.data)     
      while i < count:
        startTime = self.data[i][0] - interval /2
        endTime = startTime + interval
        if startTime > self.data[-1][0]:
          break
        if startTime < self.data[0][0]:
          startTime = self.data[0][0]
        if endTime > self.data[-1][0]:
          endTime = self.data[-1][0]
        quality = self.data[i][2]
        n = 0
        sum = 0
        while self.data[i+n][0] <= endTime:
          sum += self.data[i+n][1]
          n += 1
          if i+n >= count:
            break
        if n != 0:
          _data.append([self.data[i][0],sum/n,quality])
        i+=1
    except Exception,e:
      self.status = str(e)
    return timeSeries(_data)


  #Calculates the percentage of two timeseries
  #numerator : self
  #denominator : denom
  #returns a timeseries object of percentages
  def percent(self,denom):
    _data = []
    denom_data = {}
    try:
      #turn denominator data into a dictionary and filter out zeros (no division by 0 allowed!)
      for line in denom.data:
        if line[1] != 0:
          denom_data[line[0]] = line
      for line in self.data:
        key = line[0] 
        if key in denom_data:
          _data.append([line[0],100*float(line[1]/denom_data[key][1]),line[2]])
    except Exception,e:
      self.status = str(e)
      return timeSeries()
    return timeSeries(_data)

  #Snaps a timeseries
  #interval: interval at which time series is snapped
  #buffer : lookahead and lookback 
  #returns a snapped timeseries
  def snap(self,interval,buffer,starttime = None):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      if buffer > interval/2:
        buffer = interval/2
      #setup the initial start time
      endtime = self.data[-1][0]
      if starttime != None:
        t = starttime
      else:
        t = self.data[0][0]
      while t <= endtime:
        tlist = []
        for line in self.data:
          if line[0] >= t - buffer:
            if line[0] <= t+ buffer:
              tlist.append(line)
            else:
              break
        if len(tlist) > 0: 
          tline = tlist[0]
          for line in tlist:
            curdiff = abs(tline[0] - t).seconds
            newdiff = abs(line[0] - t).seconds
            if (curdiff > newdiff):
              tline = line
          _data.append([t,tline[1],tline[2]])
        t += interval
    except Exception,e:
      self.status = str(e)
      return timeSeries()
    return timeSeries(_data)

  #Shifts each timestamp a given time interval
  #tdelta: timedelta to shift
  #returns a timeseries object
  def timeshift(self,tdelta):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      for line in self.data:
        _data.append([line[0]+tdelta,line[1],line[2]])
    except Exception,e:
      self.status = str(e)
      print e
      return timeSeries()
    return timeSeries(_data)
            
  #Performs an operation on self
  #op: lambda function to perform eg lambda x,y: x+y
  #operand: could be a timeseries or a float
  #returns a timeseries object
  def operation(self,op,operand):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      if type (operand) is float:
        for line in self.data:
          _data.append([line[0],op(line[1],operand),line[2]])
      else:
        for line in self.data:
          val = operand.findValue(line[0])
          if val != None:
            _data.append([line[0],op(line[1],val),line[2]])
    except Exception,e:
      self.status = str(e)
      print e
      return timeSeries()
    return timeSeries(_data)

  #culls data from self
  #op: lambda function to perform eg lambda x,y: x>y
  #operand: could be a timeseries or a float
  #returns a timeseries object
  def cull(self,op,operand):
    _data = []
    if self.data == []:
      return timeSeries()
    try:
      if type (operand) is float:
        for line in self.data:
          if op(line[1],operand):
            _data.append(line)
      else:
        for line in self.data:
          val = operand.findValue(line[0])
          if val != None:
            if op(val,operand):
              _data.append([line])
    except Exception,e:
      self.status = str(e)
      print e
      return timeSeries()
    return timeSeries(_data)

class dataService:
  def __init__ (self):
    #initialize with Default Configuration
    self.status = "OK"
    self.configuration = self.getDefaultConfiguration()
    #Database Cursors
    self.dbconn = None

  #This method connects to the database
  def connect(self):
    try :
      dbname = self.configuration["dbname"]
      self.dbconn = cx_Oracle.Connection(user=self.configuration["dbuser"], password=self.configuration["dbpassword"], dsn=dbname)
      if not self.dbconn : 
        self.status = "\nCould not connect to %s\n" % dbname
        self.status += "\n%s"
    except Exception,e:
        self.status = "\nCould not connect to %s\n" % dbname
        self.status += "\n%s"+str(e)
      

  #This method disconnects from the database
  def disconnect(self):
    self.dbconn.close()

  #This method sets up the default configuration
  def getDefaultConfiguration (self):
    conf = {}
    conf ["timeFormat"] = "%d-%b-%Y %H%M" #Time format 
    conf ["timeZone"] = "GMT"
    conf ["dbuser"] = ""
    conf ["dbpassword"] = ""
    conf ["dbname"] = self.getDBname()
    conf ["office"] = "NWDP"
    conf ["defaultUnits"] = { 'depth':'ft',
      'depth-swe' :'in',
      'elev':'ft',
      'flow':'cfs',
      'head':'ft',
      'opening':'ft',
      'power':'MW',
      'precip':'in',
      'pres':'mm-hg',
      'speed':'mph',
      'stage':'ft',
      'stor':'ac-ft',
      'temp':'F',
      'dir':'deg',
      'travel':'mi',
      'rad':'langley',
      '%':'%' }
    return conf

  def updateConfiguration (self,newConf):
    for key in newConf:
      self.configuration[key] = newConf[key]
    if self.configuration["dbname"] == "detect":
      self.configuration["dbname"] = self.getDBname()

  #Determine which database to connect to
  #Currently this determines the local DB based on the domain name
  #TODO: Add functionality to fail over to another database
  def getDBname (self):
    return os.uname()[1].upper()[0:3] #determine which database to connect to
        
  #takes a pathname data dictionary compliant pathname and returns default units
  def getDefaultUnits (self,tsid):
    try:
      tsid = tsid.lower()
      tokens = tsid.split(".")
      #check to see if full Parameter is in default units and return
      param = tokens[1]
      if param in self.configuration["defaultUnits"]:
        return self.configuration["defaultUnits"][param]
      #check to see if parameter is in default units and return
      param = tokens[1].split("-")[0]
      if param in self.configuration["defaultUnits"]:
        return self.configuration["defaultUnits"][param]
    except:
      pass
    #Default to database default
    return ""

  #Reads a time series from the database#
  #tsid       - string
  #start_time - datetime
  #end_time   - datetime
  #in_units   - string
  def readTS (self, tsid, start_time, end_time, units):
    timefmt = self.configuration["timeFormat"]
    timezone = self.configuration["timeZone"]
    office = self.configuration["office"] 
    try:
      crsr = self.dbconn.cursor()
      # retrieve the time series data #
      ts_cur = self.dbconn.cursor()
      if units.lower() == "default":
        units = self.getDefaultUnits(tsid)
      crsr.execute('''
          begin
          cwms_ts.retrieve_ts(
                P_AT_TSV_RC =>:ts_cur,
                P_CWMS_TS_ID =>:tsid,
                P_UNITS =>:units,
                P_START_TIME =>to_date(:start_time, 'dd-mon-yyyy hh24mi'),
                P_END_TIME =>to_date(:end_time,   'dd-mon-yyyy hh24mi'),
                P_TIME_ZONE =>:timezone,
                P_OFFICE_ID =>:office);
          end;''', [ts_cur, tsid, units, start_time.strftime(timefmt), end_time.strftime(timefmt), timezone, office])
      records = ts_cur.fetchall()
      ts_cur.close()
      crsr.close()
    except Exception, e:
      self.status = "\nCould not retrieve "+tsid
      self.status += "\n%s" % str(e)
      return[]  
    return records

  def readLocationLevel (self, levelID, start_time, end_time, units):
    sqlStr = '''
    declare
       l_start_time date := to_date('$start_time$', 'dd-mon-yyyy hh24mi');
       l_end_time   date := to_date('$end_time$', 'dd-mon-yyyy hh24mi');
       l_interval   number := 1;
       l_dates      cwms_t_date_table;
       l_values     cwms_t_double_tab;
    begin
       select l_start_time + (level-1) * l_interval
         bulk collect
         into l_dates
         from dual
      connect by level <= (l_end_time - l_start_time) / l_interval + 1;
       l_values := cwms_level.retrieve_loc_lvl_values3(
          p_specified_times   => l_dates, 
          p_location_level_id => '$levelID$', 
          p_level_units       => '$units$', 
          p_timezone_id       => '$timezone$', 
          p_office_id         => '$office$');
       for i in 1..l_dates.count loop
          dbms_output.put_line(
             to_char(l_dates(i), 'dd-mon-yyyy hh24mi')
             ||':'
             ||cwms_rounding.round_dn_f(l_values(i), '9999999999'));
       end loop;        
    end;'''
    timefmt = self.configuration["timeFormat"]
    timezone = self.configuration["timeZone"]
    office = self.configuration["office"] 
    try:
      if units.lower() == "default":
        units = self.getDefaultUnits(levelID)
      sqlStr=sqlStr.replace('$start_time$',start_time.strftime(timefmt)).replace('$end_time$',end_time.strftime(timefmt))
      sqlStr=sqlStr.replace('$levelID$',levelID).replace('$units$',units).replace('$timezone$',timezone).replace('$office$',office)
      crsr = self.dbconn.cursor()
      crsr.callproc("dbms_output.enable")
      crsr.execute(sqlStr)
      line = crsr.var(cx_Oracle.STRING)
      status = crsr.var(cx_Oracle.NUMBER)
      records = []
      while True:
        crsr.callproc("dbms_output.get_line",(line,status))
        if status.getvalue() != 0:
          break
        else:
          tokens = line.getvalue().split(":")
          tokens [0] = datetime.datetime.strptime(tokens[0],timefmt)
          tokens [1] = float(tokens[1])
          tokens.append(0)
          records.append(tokens)
    except Exception, e:
      self.status = "\nCould not retrieve "+levelID
      self.status += "\n%s" % str(e)
      return[]  
    return records



  def writeToCWMS (self,tsid,units,valueList):
    crsr = self.dbconn.cursor()
    office = self.configuration["office"] 
    timefmt = self.configuration["timeFormat"]
    timezone = self.configuration["timeZone"]
    office = self.configuration["office"] 
    if units.lower() == "default":
      units = self.getDefaultUnits(tsid)

    try:
      SQLstr  ="declare\n"
      SQLstr +="      ts     timestamp(6);\n"
      SQLstr +="      tstz   timestamp(6) with time zone;\n"
      SQLstr +="      val    binary_double;\n"
      SQLstr +="            qual   number;\n"
      SQLstr +="            l_tsv  cwms_20.tsv_array := cwms_20.tsv_array();\n"
      SQLstr +="          begin\n"
      i = 0
      for line in valueList:
        i += 1
        timestamp = line[0].strftime(timefmt).upper()
        value = str(line[1])
        quality = str(line[2])
        SQLstr +="            ts   := to_timestamp('"+timestamp+"','DD-MON-YYYY HH24MI');\n"
        SQLstr +="            tstz := from_tz(ts,'"+timezone+"');\n"
        SQLstr +="            val  := "+value+";\n"
        SQLstr +="            qual := "+quality+";\n"
        SQLstr +="            l_tsv.extend;\n"
        SQLstr +="            l_tsv("+str(i)+") := cwms_20.tsv_type(tstz, val, qual);\n"
      SQLstr +="            cwms_20.cwms_ts.store_ts('"+tsid+"','"+units+"',l_tsv,'REPLACE ALL',null,null,'"+office+"');\n"
      SQLstr +="          commit;\n"
      SQLstr +="          end;\n"
      crsr.execute(SQLstr)
    except Exception, e:
      self.status = "\nCould not store "+tsid
      self.status += "\n%s" % str(e)
    crsr.close()

  #This breaks the TS into chunks
  def writeToCWMS2 (self,tsid,units,valueList):
    crsr = self.dbconn.cursor()
    office = "NWDP"
    timefmt = self.configuration["timeFormat"]
    timezone = self.configuration["timeZone"]
    office = self.configuration["office"]
    if units.lower() == "default":
      units = self.getDefaultUnits(tsid)
    print "units:"+units
    buffersize = 1500
    try:
      done = False
      i = 0
      while done == False:
        count = 1
        SQLstr  ="declare\n"
        SQLstr +="  ts     timestamp(6);\n"
        SQLstr +="  tstz   timestamp(6) with time zone;\n"
        SQLstr +="  val    binary_double;\n"
        SQLstr +="  qual   number;\n"
        SQLstr +="  l_tsv  cwms_20.tsv_array := cwms_20.tsv_array();\n"
        SQLstr +="  begin\n"
        j = i+buffersize
        if j > len(valueList):
          j = len (valueList)
          done = True
        if i == j:
          break
        for k in xrange (i,j):
          line = valueList[k]
          timestamp = line[0].strftime(timefmt).upper()
          value = str(line[1])
          quality = str(line[2])
          SQLstr +="    ts   := to_timestamp('"+timestamp+"','DD-MON-YYYY HH24MI');\n"
          SQLstr +="    tstz := from_tz(ts,'"+timezone+"');\n"
          SQLstr +="    val  := "+value+";\n"
          SQLstr +="    qual := "+quality+";\n"
          SQLstr +="    l_tsv.extend;\n"
          SQLstr +="    l_tsv("+str(count)+") := cwms_20.tsv_type(tstz, val, qual);\n"
          count += 1
        SQLstr +="    DBMS_OUTPUT.ENABLE(1000000);\n"
        SQLstr +="    cwms_20.cwms_ts.store_ts('"+tsid+"','"+units+"',l_tsv,'REPLACE ALL',null,null,'"+office+"');\n"
        SQLstr +="    commit;\n"
        SQLstr +="end;\n"
        crsr.execute(SQLstr)
        sys.stdout.write("wrote: "+str(i+count)+" values.\r")
        i += buffersize
    except Exception, e:
      self.status = "\nCould not store "+tsid
      self.status += "\n%s" % str(e)
      print self.status
    crsr.close()


  #gets status message of object and resets it to "OK"  
  def getStatus(self):
    s = self.status
    self.status = "OK"
    return s

class rdb:
  #construtor rewrites a path to a RDB file
  def __init__ (self, path):
    #initialize with Default Configuration
    self.status = "OK"
    #format = INDEP   SHIFT   DEP     STOR
    self.data = self.loadRDB (path)

  def loadRDB (self,path):
    output = []
    self.path = path
    try:
      input = open (path,"r")
      for line in input:
        if (not "#" in line) and (len(line) > 1):
          output.append(line.split("\t"))
    except Exception, e:
      self.status = "\n%s" % str(e)
    return output[2:]

  #interpolate values
  #This may be changed to a higher order interpolation in the future
  def interpolateValue(self, x0, y0, x1, y1, x):
    m = (y1 - y0) / (x1 - x0)
    output = y0 + (x - x0) * m
    return output

  def rate (self, indep):
    data = self.data
    index = len(data)-2
    for i in xrange(len(data)-1):
      if indep < float(data[i+1][0]):
        index = i
        break
    return self.interpolateValue(float(data[index][0]),float(data[index][2]),float(data[index+1][0]),float(data[index+1][2]),indep)

  #This switches the domain and range of the RDB and rates it.
  def rate2 (self, indep):
    data = self.data
    index = len(data)-2
    for i in xrange(len(data)-1):
      if indep < float(data[i+1][2]):
        index = i
        break
    return self.interpolateValue(float(data[index][2]),float(data[index][0]),float(data[index+1][2]),float(data[index+1][0]),indep)

  def rateTS (self,ts):
    output = []
    for line in ts.data:
      output.append([line[0],self.rate(line[1]),line[2]])
    return timeSeries(output)

  def rateTS2 (self,ts):
    output = []
    for line in ts.data:
      output.append([line[0],self.rate2(line[1]),line[2]])
    return timeSeries(output)


class tablegrid:
  #construtor rewrites a path to a RDB file
  def __init__ (self, path):
    #initialize with Default Configuration
    self.status = "OK"
    self.path = None
    self.data = self.loadTable (path)

  def loadTable (self,path):
    output = []
    try:
      self.path = path
      input = open (path,"r")
      for line in input:
        if (not "#" in line) and (len(line) > 1):
          row2 = []
          if "," in line:
            row1 = line.strip().split(",")
          else:
            row1 = line.strip().split("\t")
          for n in row1:
            row2.append(float(n)) #Iterate and convert entries to floating point number
          output.append (row2)
    except Exception, e:
      self.status = "\n%s" % str(e)
    return output   

  def tableLookup (self, arr, colval, rowval):
    #Seek the coordinates
    output = 0
    x = 0
    y = 0
    maxcols = len(arr[0])-1
    maxrows = len(arr)-1
    x = maxcols-1 #default to end of list if not found
    y = maxrows-1
    i = 1
    while (i < maxcols): #seeking coordinates for column values
      if arr[0][i+1] > colval:
        x = i
        i = maxcols #exit loop
      i+=1
    i = 1 
    while (i < maxrows): #seeking coorinate for row values
      if arr[i+1][0] > rowval: 
        y = i
        i = maxrows #exit loop
      i+=1
    if ((x == maxcols) or (y == maxrows)):
      output = arr[y][x]
    else: 
      output = self.bilinear(arr[0][x], arr[y][0], arr[0][x + 1], arr[y + 1][0], arr[y][x], arr[y + 1][x], arr[y][x + 1], arr[y + 1][x + 1], colval, rowval);
    return output

  def bilinear(self, x1, y1, x2, y2, fQ11, fQ12, fQ21, fQ22, x, y):
    retval = (fQ11 / ((x2 - x1) * (y2 - y1))) * (x2 - x) * (y2 - y) + (fQ21 / ((x2 - x1) * (y2 - y1))) * (x - x1) * (y2 - y) + (fQ12 / ((x2 - x1) * (y2 - y1))) * (x2 - x) * (y - y1) + (fQ22 / ((x2 - x1) * (y2 - y1))) * (x - x1) * (y - y1)
    return retval
  
  #this takes 2 timseries objects and rates them
  def rateTS (self,cols,rows):
    output = []
    for line in cols.data:
      rowval = rows.findValue(line[0])
      if rowval != None:
        output.append([line[0],self.tableLookup(self.data,line[1],rowval),line[2]])
    return timeSeries(output)
