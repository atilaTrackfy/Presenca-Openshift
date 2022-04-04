import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from fortPosition import presencemod
from sklearn import preprocessing
import time
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BigInteger, String, desc
from sqlalchemy.sql import select

def createDatabaseEngine():
    eng = sqlalchemy.create_engine("postgresql://trackfy:Rq4KwKctSCKePJyJ@172.30.227.104:5432/sampledb")
    return eng

def createTable(engine):
    meta = MetaData()
    localTable = Table(
        'local', meta, 
        Column('id', Integer, primary_key = True), 
        Column('local', String), 
        Column('beacon', String),
        Column('ts', BigInteger),
    )

    insp = sqlalchemy.inspect(engine)
    
    if not insp.has_table("local", schema="public"):
        meta.create_all(engine)
    else:
        print("Tem tabela")

    return localTable

def checkLastTimeStamp (eng, localTable):
    lastTs = 0
    slct = select(localTable.c.ts).order_by(desc(localTable.c.ts)).limit(1)
    result = eng.execute(slct)
    row = result.fetchone()

    if len(row) > 0:
        lastTs = row[0]
    
    result.close()
    return lastTs

def grabRawData(conn, lastTS):
    query = f"select * from scan where ts > {lastTS} order by ts LIMIT 10000"
    table = pd.read_sql_query(query, conn)
    return table

def grabScannerList(table):
    scannerList = list(set(table.scanner.values))
    return scannerList

def calculatePresence():
    eng    = createDatabaseEngine()
    if eng:
        localTable   = createTable(eng)
        lastTS       = checkLastTimeStamp(eng, localTable)
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

            locationDtFrame = pd.DataFrame({'local': location})
            tableProcData             = tableRawData[ ['ts', 'beacon'] ]
            joinedtFrame = locationDtFrame.join(tableProcData)
            joinedtFrame.to_sql('local', eng, index=False, if_exists='append', chunksize=1000)

        return isThereData
    return conn

if __name__ == "__main__":

    print("Starting Application")
    #while True:
    isThereData = calculatePresence()
        #if not isThereData:
            #time.sleep(120)

