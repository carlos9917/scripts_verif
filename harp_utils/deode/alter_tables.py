"""
Crude script to convert the DEOD tables from the new
to the old format

"""

import sqlite3
import pandas as pd

param = sys.argv[1]
infile = sys.argv[2]

conn = sqlite3.connect("new/FCTABLE_T2m_202312_00_TEST.sqlite")
cursor = conn.cursor()

sql_command = "SELECT * FROM FC"
df_new = pd.read_sql(sql_command, conn)

model = "DEOD"
replace_columns = {"fcst_dttm": "fcdate", "lead_time": "leadtime",param :"p",model:model+"_det","valid_dttm":'validdate'}

# Replace 'old_column_name' and 'new_column_name' with your actual column names
for column in replace_columns.keys():
    new_column = replace_columns[column]
    query = f"ALTER TABLE FC RENAME COLUMN {column} TO {new_column};"
    cursor.execute(query)
    conn.commit()

# Replace 'old_index_name' and 'new_index_name' with your actual index names
query_create_index = "CREATE UNIQUE INDEX index_fcdate_leadtime_SID ON FC (fcdate,leadtime,SID);"
cursor.execute(query_create_index)

# Replace 'old_index_name' with your actual index name
query_drop_index = "DROP INDEX IF EXISTS index_fcst_dttm_lead_time_SID;"
cursor.execute(query_drop_index)
conn.close()

# Below I change the data types of the table
# Connect to the SQLite database
conn = sqlite3.connect("new/FCTABLE_T2m_202312_00_TEST.sqlite")
cursor = conn.cursor()

# Create a new table with the desired changes, including the column type modification
new_table_query = """
CREATE TABLE FC_new (
    fcdate INT,    
    leadtime INT,
    parameter TEXT,
    SID INT, 
    lat DOUBLE, 
    lon DOUBLE, 
    model_elevation DOUBLE, 
    p DOUBLE, 
    units TEXT, 
    validdate INT, 
    DEODE_det DOUBLE

);
"""
cursor.execute(new_table_query)

# Copy data from the old table to the new one
copy_data_query = "INSERT INTO FC_new SELECT fcdate, CAST(leadtime AS INTEGER), parameter, SID, lat, lon, model_elevation, p, units, validdate, DEOD_det FROM FC;"
cursor.execute(copy_data_query)

# Drop the old table
drop_old_table_query = "DROP TABLE FC;"
cursor.execute(drop_old_table_query)

# Replace 'old_index_name' and 'new_index_name' with your actual index names
query_create_index = "CREATE UNIQUE INDEX index_fcdate_leadtime_SID ON FC_new (fcdate,leadtime,SID);"
cursor.execute(query_create_index)


#rename it again
rename_table_query = "ALTER TABLE FC_new RENAME TO FC;"
cursor.execute(rename_table_query)
# Commit changes and close the connection
conn.commit()
conn.close()





