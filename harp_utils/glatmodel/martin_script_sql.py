"""
Script provided by Martin Petras in the slack channel
"""
import sqlite3
 
def createSqlite(x):

    sqlite_name = f"OBSTABLE_{x}.sqlite"
    connection = sqlite3.connect(sqlite_name) # file path
 
    # create a cursor object from the cursor class
    cur = connection.cursor()
 
    cur.execute('''
    CREATE TABLE SYNOP(
       validdate integer, 
       SID integer, 
       lat real,
       lon real,
       elev real,
       T2m real,
       RH2m real,
       Q2m real,
       D10m real,
       S10m real
   )''')

    cur.execute('''
    CREATE TABLE SYNOP_params(
       parameter varchar, 
       accum_hours real,
       units varchar
   )''')


    cur.execute('''
    CREATE UNIQUE INDEX index_validdate_SID ON SYNOP(
        validdate,
        SID
    )''')
 
    print("\nDatabase created successfully!!!")
    # committing our connection
    connection.commit()
 
    # close our connection
    connection.close()
