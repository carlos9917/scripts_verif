#/bin/bash

year=2021

for filename in $fcst_path/$year/*; do
    echo $filename
    python3 restructure_db.py --file=$filename 0 1
done

mkdir sql_dbs/FCTABLE/glatmodel/$year
echo $year
for month in $(seq -f "%02g" 12 )
do
	mkdir sql_dbs/FCTABLE/glatmodel/$year/$month
	cp sql_dbs/FCTABLE/glatmodel/*$year$month* sql_dbs/FCTABLE/glatmodel/$year/$month
done




