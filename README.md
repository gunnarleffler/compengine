compengine
==========

Supplemental Timeseries Computation Engine

How to install compengine
-------------------------
Ensure the $LD_LIBRARY_PATH contains the following:
/usr/openwin/lib:/usr/cwms/lib:/usr/local/lib:/usr/lib:/usr/local/ssl/lib:/oraclebase/product/11.1_client/lib32:/usr/cwms/java/jre/lib/sparc:/usr/sfw/lib/

If it hasn't been already, download and install python 2.7.3
------------------------------------------------------------
unzip/tar it and in the appropriate directory compile:

./configure
make
make install



If it hasn't been already, download and install cx_Oracle
---------------------------------------------------------
python setup.py build
python setup.py install