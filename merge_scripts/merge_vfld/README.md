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

