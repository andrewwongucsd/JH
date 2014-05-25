#!/usr/bin/env python
from globalvar import *
from database import *
from dbconn import *
from random import random
from multiprocessing import Pool
import re

def createProxyTables():
    try:
        conn = getConn()
        cur = conn.cursor()
        cur.execute("CREATE TABLE proxies (id SERIAL NOT NULL, ip TEXT NULL, port INT NULL, type INT NULL, rating DOUBLE PRECISION NULL, PRIMARY KEY (id))")
        conn.commit()
        cur.close()
        conn.close()
        conn = None
        return True
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False
        
def importProxies(proxyFilePath):
    try:
        with open(proxyFilePath) as proxyFile:
            content = proxyFile.read()
            content = re.sub("(\r\n)|(\r)", "\n", content)
            contentLines = re.split("\n", content)
            proxies = [re.split(":", contentLine) for contentLine in contentLines if contentLine != ""]
            with Pool(processes = int(getSetting("databaseThreads"))) as pool:
                results = pool.map(addProxy, proxies)
        return sum([1 for result in results if result])
    except FileNotFoundException as e:
        print(e)
        return 0
        
def addProxy(proxy):
    success = False
    conn = getConn()
    cur = conn.cursor()
    data = (proxy[0], int(proxy[1]), int(proxy[2]))
    cur.execute("SELECT * FROM proxies WHERE ip=%s AND port=%s AND type=%s", data)
    if not cur.fetchone():
        print("Adding proxy {0}".format(proxy))
        data = (proxy[0], int(proxy[1]), int(proxy[2]), 10)
        cur.execute("INSERT INTO proxies (ip, port, type, rating) VALUES (%s,%s,%s,%s)", data)
        conn.commit()
        success = True
    else:
        print("Proxy {0} exists".format(proxy))
    cur.close()
    conn.close()
    conn = None
    return success

def getProxy():
    try:
        conn = getConn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM proxies ORDER BY id DESC")
        proxies = cur.fetchall()
        cur.close()
        conn.close()
        conn = None
        y = 0
        for proxy in proxies:
            y += proxy[4]/proxy[4]/proxy[4]
        while 1:
            for proxy in proxies:
                if proxy[4]/proxy[4]/proxy[4] > y*random():
                    return proxy
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False

def multiplyRating(id, mul):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (id,)
        cur.execute("SELECT rating FROM proxies WHERE id=%s", data)
        origRating = cur.fetchone()[0]
        if origRating*mul < ratingThreshold:
            newRating = ratingThreshold
        else:
            newRating = origRating*mul
        data = (newRating, id)
        if newRating > origRating:
            print("New rating: {1}{0}{2}".format(round(newRating, 3), bcolors["FAIL"], bcolors["ENDC"]))
        else:
            print("New rating: {1}{0}{2}".format(round(newRating, 3), bcolors["OKGREEN"], bcolors["ENDC"]))
        cur.execute("UPDATE proxies SET rating=%s WHERE id=%s", data)
        conn.commit()
        cur.close()
        conn.close()
        conn = None
        return True
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False