import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from fortPosition import presencemod
from sklearn import preprocessing
import time
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

def connectDatabase():
    try:
        conn = psycopg2.connect("host=172.30.227.104 port=5432 dbname=sampledb user=trackfy password=Rq4KwKctSCKePJyJ")
        #engine = sqlalchemy.create_engine('postgresql://postgres:test1234@localhost:5432/sql-shack-demo')
        # conn = psycopg2.connect("host=localhost port=5432 dbname=experiment user=postgres password=postgres")
        print("Connected!")
        return conn
    except psycopg2.OperationalError:
        print('Connection not established to PostgreSQL.')
        return False

    # print("Connected!")
    # if conn is not None:
        # print('Connection established to PostgreSQL.')
        # return conn
    # else:
        # print('Connection not established to PostgreSQL.')
        # return False

def createDatabaseEngine():
    eng = sqlalchemy.create_engine("postgresql://trackfy:Rq4KwKctSCKePJyJ@172.30.227.104:5432/sampledb")
    return eng

def createTable(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS LOCAL
            (ID             SERIAL,
            LOCAL           CHAR(17)    NOT NULL,
            BEACON          CHAR(17)    NOT NULL,
            TS              BIGINT      NOT NULL,
            CONSTRAINT local_pkey PRIMARY KEY (ID));
    """)

def checkLastTimeStamp (cursor):
    cursor.execute("select ts from local order by ts desc limit 1")
    if cursor.rowcount > 0:
        return cursor.fetchone()[0]
    else:
        return 0

def grabRawData(conn, lastTS):
    query = f"select * from scan where ts > {lastTS} order by ts LIMIT 10000"
    table = pd.read_sql_query(query, conn)
    return table

def grabScannerList(table):
    scannerList = list(set(table.scanner.values))
    return scannerList

def calculatePresence():
    conn   = connectDatabase()
    eng    = createDatabaseEngine()
    if conn:
        cursor = conn.cursor()
        createTable(cursor)
        lastTS       = checkLastTimeStamp(cursor)
        tableRawData = grabRawData(eng, lastTS)
        isThereData  = not tableRawData.empty
        if isThereData:
            scannerList  = grabScannerList(tableRawData)
            scannerList  = [ "???" ] + scannerList
            le           = preprocessing.LabelEncoder()
            le.fit(scannerList)
            scannerListLabel = le.transform(scannerList)
            scannerLabel     = le.transform(tableRawData.scanner.values)

            location = le.inverse_transform(
                         presencemod.presence(
                             n=len(tableRawData.ts.values),
                             windowtimelength=30000,
                             ts=tableRawData.ts.values,
                             rssi=tableRawData.rssi.values,
                             scanner=scannerLabel,
                             numscanners=len(scannerListLabel),
                             scannerlist=scannerListLabel
                             )
                         )

            #tableProcData             = tableRawData[ ['ts', 'beacon'] ]
            #tableProcData.loc['scanner'] = location

            print(scannerListLabel)

        return isThereData
    return conn

if __name__ == "__main__":

    print("Starting Application")
    #while True:
    x = 0
    while x < 10: 
        isThereData = calculatePresence()
        if not isThereData:
            time.sleep(120)
        x = x + 1
