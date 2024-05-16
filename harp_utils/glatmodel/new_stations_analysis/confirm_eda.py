"""
just a sanity check to confirm the summary done for station
counts in R makes sense.

"""
import pandas as pd
import sqlite3
dbase ="OBSTABLE/OBSTABLE_TROAD_2023.sqlite"
con = sqlite3.connect(dbase)
com = "SELECT * FROM SYNOP"
df = pd.read_sql(com,con)

#convert to datetime object
df['unixtime'] = df["valid_dttm"]
df['valid_dttm'] = pd.to_datetime(df['valid_dttm'], unit='s')
# Extract hour from 'valid_dttm'
df['hour'] = df['valid_dttm'].dt.hour

# Extract date from 'valid_dttm'
df['date'] = df['valid_dttm'].dt.date
# Group by 'SID', 'hour', and 'date' and count instances of 'TROAD'
start_date = pd.Timestamp(2023, 1, 1)
end_date = pd.Timestamp(2023, 1, 31)
df_one_month = df[(df['valid_dttm'] >= start_date) & (df['valid_dttm'] <= end_date)]
result = df_one_month.groupby(['SID', 'hour'])['TROAD'].count().reset_index()

# check one station
import pdb
pdb.set_trace()
