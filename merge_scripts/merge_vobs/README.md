Merge for upscaled data 

source1: 
--------
Directory 
/netapp/dmiusr/aldtst/upscale/igb40h11
which contains files with names like

vups06igb40h11201905300048
vups12igb40h11201905300048
vups36igb40h11201905300048


where 06, 18 and 36 refers to number of grid point corresponding to an upscaling distance of 15, 45, 90 km.

freq: every 3 h, format YYYYMMDDHHXX, with XX from 00 to 66
vups06igb40h11201905011262

source2:
--------
Directory 
/netapp/dmiusr/aldtst/upscale/sgl40h11
which contains files
vups20sgl40h11201905300048
vups60sgl40h11201905300048
vups120sgl40h11201905300048

where 20, 60 and 120 refers to number of grid point corresponding to an upscaling distance of 15, 45, 90 km. 
The model SGL40h11 has *only* 20 stations.

Merging objective: 
------------------
For each of the data file in igb40h11 with name
vups06igb40h11$DTG$LL
the content for the 20 overlapped stations shall be overwritten by those from sgl40h11
vups12sgl40h11$DTG$LL

and likewise, 
vups18igb40h11$DTG$LL
merged by
vups60sgl40h11$DTG$LL

 
vups36igb40h11$DTG$LL
the content for the 20 overlapped stations shall be overwritten by those from sgl40h11
vups120sgl40h11$DTG$LL

New data set
-----------------


out vup06gl_hm----
from tassilaq

2019060303


