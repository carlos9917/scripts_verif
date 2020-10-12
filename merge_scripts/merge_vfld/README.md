Merging vfld data from 750m models into IGB data

merging of 750m data
Second, make a 750m model-only vfld data collection, 'gl750', with file names vfldgl750201907150024, merging data from 
/netapp/dmiusr/aldtst/vfld/tasii
/netapp/dmiusr/aldtst/vfld/sgl40h11
/netapp/dmiusr/aldtst/vfld/nuuk750
/netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)

merge_vfld.pl: does not work as it is. 

vfld_lite.py: class to contain all data from a vfld file
-------------------------------
# 202005

- merge_750models.py will merge all 

$py3 ./merge_750models.py -pe 20190102-20190131 -fl 52 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir


---------------------
# 20200506

- Merge the models in this order
IGB (reference)
gl_opr (IGB+TASII+SGL40h11)
gl_hires (IGB + TASII + SGL40h11 +  "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" 
on-demand ("sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" )


---------------------------------------
# Instructions on how to use run_merge_on_demand.sh


Copy the following files from my repo:

/home/cap/verify/scripts_verif/merge_scripts/merge_vfld

vfld.py
merge_on_demand_750.py
run_merge_on_demand.sh

to your directory.

These are the only files needed to run the processing at DMI.
The rest are scripts used for the CARRA streams.


Then edit the pbs script:

run_merge_on_demand.sh

where you need to change the period of processing
(do not use more than one month or it will take forever).

The variables are more or less self-explanatory.

You need to change these:

scrdir= the path where scripts are located

outdir= the path where you want to write the data (the script will create a separate directory for each different output model)

date_ini = init date (YYYYMMDD)

date_end = final date (YYYYMMDD)

flen = length of the forecast

logfile= a log file with some debugging output from merge_on_demand_750.py 
Most of the screen output will be written to this file.
