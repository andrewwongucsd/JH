#!/usr/bin/env python
from random import shuffle
from dbconn import *
import time

def createTables():
    try:
        conn = getConn()
        cur = conn.cursor()
        cur.execute("CREATE TABLE attackedPosts (rowID SERIAL NOT NULL, centID INT NULL, postID INT NULL, timeStamp INT NULL, PRIMARY KEY (rowID) )")
        cur.execute("CREATE TABLE centsList (centID INT NOT NULL, message TEXT NULL, PRIMARY KEY (centID) )")
        cur.execute("CREATE TABLE settings (setting CHAR(64) NOT NULL, value VARCHAR(128) NULL, PRIMARY KEY (setting) )")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('email', 'akw003@ucsd.edu')")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('password', 'lemonhkg')")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('postIDLowerLimit', 5000000)")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('postedSleepTime', 20)")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('generalTimeout', 30)")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('workerSleepTime', 60)")
        cur.execute("INSERT INTO settings (setting, value) VALUES ('databaseThreads', 16)")
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

def areTablesExist():
    try:
        conn = getConn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM attackedPosts")
        cur.execute("SELECT * FROM centsList")
        cur.execute("SELECT * FROM settings")
        cur.close()
        conn.close()
        conn = None
        return True
    except psycopg2.ProgrammingError:
        conn.rollback()
        conn.close()
        conn = None
        return False

def getSetting(setting):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (str(setting),)
        cur.execute("SELECT value FROM settings WHERE setting=%s", data)
        val = cur.fetchone()[0]
        cur.close()
        conn.close()
        conn = None
        return val
    except psycopg2.OperationalError: 
        conn.rollback()
        conn.close()
        conn = None
        return False
    except psycopg2.InterfaceError as e:
        print(e)
        return False
        
def changeSetting(setting, val):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (val,setting)
        cur.execute("UPDATE settings SET value=%s WHERE setting=%s", data)
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

def saveReplyedPost(userID, postID):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (userID, postID, time.time())
        cur.execute("INSERT INTO attackedPosts (centID, postID, timeStamp) VALUES (%s,%s,%s)", data)
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
    
cache = {}
def isThisPostReplyed(userID, postID):
    if userID in cache:
        return (postID in cache[userID])
    else:
        try:
            conn = getConn()
            cur = conn.cursor()
            data = (userID,)
            cur.execute("SELECT postID FROM attackedPosts WHERE centID=%s", data)
            cache[userID] = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            conn = None
            return (postID in cache[userID])
        except psycopg2.OperationalError:
            conn.rollback()
            conn.close()
            conn = None
            return False

def getWeapon(userID):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (userID,)
        if userID in getCentsList():
            cur.execute("SELECT message FROM centsList WHERE centID=%s", data)
            msg = cur.fetchone()[0]
            cur.close()
            conn.close()
            conn = None
            return msg
        else:
            cur.close()
            conn.close()
            conn = None
            return False
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False
        
def changeWeapon(userID, msg):
    try:
        conn = getConn()
        cur = conn.cursor()
        data = (msg,int(userID))
        if userID in getCentsList():
            cur.execute("UPDATE centsList SET message=%s WHERE centID=%s", data)
            conn.commit()
            cur.close()
            conn.close()
            conn = None
            return True
        else:
            cur.close()
            conn.close()
            conn = None
            return False
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False

def getCentsList():
    try:
        conn = getConn()
        cur = conn.cursor()
        cur.execute("SELECT centID FROM centsList")
        centsList = [cent[0] for cent in cur.fetchall()]
        cur.close()
        conn.close()
        conn = None
        if centsList != None and len(centsList):
            shuffle(centsList)
            return centsList
        else:
            return []
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return []

def newCent(userID, msg):
    try:
        if userID not in getCentsList():
            conn = getConn()
            cur = conn.cursor()
            data = (userID, msg)
            cur.execute("INSERT INTO centsList VALUES (%s,%s)", data)
            conn.commit()
            cur.close()
            conn.close()
            conn = None
            return True
        else:
            return False
    except psycopg2.IntegrityError as e:
        print(e)
        conn.rollback()
        conn.close()
        conn = None
        return False
        
def delCent(userID):
    try:
        if userID in getCentsList():
            conn = getConn()
            cur = conn.cursor()
            data = (userID,)
            cur.execute("DELETE FROM centsList WHERE centID=%s", data)
            conn.commit()
            cur.close()
            conn.close()
            conn = None
            return True
        else:
            return False
    except psycopg2.OperationalError:
        conn.rollback()
        conn.close()
        conn = None
        return False