Merging vfld data from 750m models into IGB data

merging of 750m data
Second, make a 750m model-only vfld data collection, 'gl750', with file names vfldgl750201907150024, merging data from 
/netapp/dmiusr/aldtst/vfld/tasii
/netapp/dmiusr/aldtst/vfld/sgl40h11
/netapp/dmiusr/aldtst/vfld/nuuk750
/netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)

merge_vfld.pl: does not work as it is. 

vfld_lite.py: class to contain all data from a vfld file
