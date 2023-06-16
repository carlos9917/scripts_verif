import sqlite3
import pandas as pd
from rich import print
from datetime import datetime

obs="/data/projects/glatmodel/verification/harp/OBSTABLE/OBSTABLE_S10m_2023.sqlite"
con=sqlite3.connect(obs)
df_out = pd.read_sql('SELECT * FROM SYNOP;', con)
#print(df_out[df_out["SID"]==1018])
con.close()
#check the dates
print(f"Checking the dates in {obs}")
df_out["datetime"] = pd.to_datetime(df_out["validdate"],unit="s")
start_date=datetime(2023,3,1)
end_date=datetime(2023,3,31)
print("summary of first and last dates")
print(df_out.head(10))
print(df_out.tail(10))
print(f"Data in the range {start_date}-{end_date}")
df_sel = df_out[(df_out["datetime"] >= start_date) & (df_out["datetime"] <= end_date)]
print(df_sel)
fc="/data/projects/glatmodel/verification/harp/FCTABLE/2023/03/FCTABLE_S10m_202303_00.sqlite"
con=sqlite3.connect(fc)
df_out = pd.read_sql('SELECT * FROM FC;', con)
df_out["datetime"] = pd.to_datetime(df_out["validdate"],unit="s")
con.close()
print(f"Checking the dates in {fc}")
print("summary of first and last dates")
print(df_out.head(10))
print(df_out.tail(10))
