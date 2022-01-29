from multiprocessing import connection
import sqlite3
import hashlib
import datetime
import smokesignal

def getConnection():
    connection=sqlite3.connect("database.db")
    cursor=connection.cursor()
    return connection, cursor

def sanitize(string):
    string=string.replace(';', '').replace('\\n', '').replace('\'', '').replace('\"', '').strip()
    return string

def initializeDB():
    connection, cursor=getConnection()
    cursor.execute("CREATE TABLE users (userid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, email TEXT);")
    cursor.execute("CREATE TABLE searches (searchid INTEGER PRIMARY KEY AUTOINCREMENT, createdOn TEXT, userid INTEGER, searchimages TEXT, initialsearchstatus TEXT, reversesearchstatus TEXT, oneoff BOOL);")
    connection.close()

def init():
    connection, cursor=getConnection()
    try:
        cursor.execute("SELECT userid FROM users;")
    except:
        initializeDB()
    connection.close()

def emailExists(email):
    connection, cursor=getConnection()
    cursor.execute("SELECT userid FROM users WHERE email='{}'".format(sanitize(email)))
    d=cursor.fetchall()
    connection.close()
    if len(d)==0:
        return False
    else:
        return True

def usernameExists(username):
    connection, cursor=getConnection()
    cursor.execute("SELECT userid FROM users WHERE username='{}'".format(sanitize(username)))
    d=cursor.fetchall()
    connection.close()
    if len(d)==0:
        return False
    else:
        return True

def createUser(username, email, password):
    connection, cursor=getConnection()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (\'{}\', \'{}\', \'{}\');".format(sanitize(username), sanitize(email), hashlib.sha256(password.encode()).hexdigest()))
        connection.commit()
        connection.close()
        return True
    except:
        return False

def checkCredentials(username, password):
    connection, cursor=getConnection()
    if not usernameExists(username):
        return -1, False
    try:
        cursor.execute("SELECT userid, username, password FROM users WHERE username=\'{}\'".format(username))
        d=cursor.fetchall()
        connection.close()
        if d[0][2]==hashlib.sha256(password.encode()).hexdigest():
            return d[0][0], True
        else:
            return -1, False
    except:
        return -1, False

def getCurrentSearches(userid):
    connection, cursor=getConnection()
    try:
        cursor.execute("SELECT searchid, createdOn, userid, searchimages, initialsearchstatus, reversesearchstatus, oneoff FROM searches WHERE userid={};".format(userid))
        d=cursor.fetchall()
        connection.close()
        return d        
    except:
        return []

def createSearch(userid, filenames, initialSearchStatus, reverseSearchStatus, oneOff):
    connection, cursor=getConnection()
    try:
        cursor.execute("INSERT INTO searches (createdOn, userid, searchimages, initialsearchstatus, reversesearchstatus, oneoff) VALUES (\'{}\', {}, \'{}\', \'{}\', \'{}\', {});".format(datetime.datetime.timestamp(datetime.datetime.now()), userid, filenames, initialSearchStatus, reverseSearchStatus, oneOff))
        connection.commit()
        cursor.execute("SELECT searchid FROM searches WHERE userid={}".format(userid))
        sid=cursor.fetchall()[-1][0]
        connection.close()
        if initialSearchStatus!="NOTREQUIRED":
            fnames=[]
            for i in filenames.split(";"):
                fnames.append("static/upload/"+i)
            smokesignal.emit('startcomparison', fnames, sid)
        return sid, True
    except:
        return -1, False

@smokesignal.on('matchfoundoninitialsearch')
def handleMatchFoundInitialSearch(matchedurl, searchid):
    connection, cursor=getConnection()
    try:
        cursor.execute("SELECT initialsearchstatus FROM searches WHERE searchid={}".format(searchid))
        d=cursor.fetchall()
        if d[0][0]=="NOTCOMPLETE" or d[0][0]=="NOTREQUIRED":
            newinitialstatus="FOUNDAT||"+matchedurl
        else:
            newinitialstatus=d[0][0]+"||"+matchedurl
        cursor.execute("UPDATE searches SET initialsearchstatus=\'{}\' WHERE searchid={}".format(newinitialstatus, searchid))
        connection.commit()
        connection.close()
        smokesignal.emit('startreversesearch', matchedurl, searchid)
    except Exception as err:
        smokesignal.emit('error', 'Could not store matchfound to database.', str(err))

def getSearch(searchid):
    connection, cursor=getConnection()
    try:
        cursor.execute("SELECT createdOn, userid, searchimages, initialsearchstatus, reversesearchstatus, oneoff FROM searches WHERE searchid={};".format(searchid))
        d=cursor.fetchall()
        connection.close()
        return d[0]
    except:
        return []

def checkSearchId(searchid):
    connection, cursor=getConnection()
    try:
        searchid=int(searchid)
        cursor.execute("SELECT createdOn FROM searches WHERE searchid={}".format(searchid))
        d=cursor.fetchall()
        connection.close()
        if len(d)==0:
            return False
        return True
    except:
        return False
