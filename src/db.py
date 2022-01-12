from psycopg2 import pool
import json
import time

f= open("config.json","r")  
settings = json.load(f)
f.close()


pool = pool.SimpleConnectionPool(1,20,**settings['database'])

async def date_check():
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reddit_posted.rising LIMIT 0")
        cols = [desc[0] for desc in cursor.description]
        if "actiondate" not in cols:
            cursor.execute("ALTER TABLE reddit_posted.rising ADD COLUMN actiondate VARCHAR ( 50 )")
            cursor.execute("ALTER TABLE reddit_posted.hot ADD COLUMN actiondate VARCHAR ( 50 )")
            connection.commit()
        cursor.close()
        pool.putconn(connection)
    else:
        print("Cant connect")
        raise "ConnectionError"


async def get_rising_posted():
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT postid FROM reddit_posted.rising")
        records = cursor.fetchall()
        cursor.close()
        pool.putconn(connection)
        records2=[]
        for i in records:
            records2.append(i[0])
        return records2
    else:
        print("Cant connect")
        raise "ConnectionError"



async def get_hot_posted():
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reddit_posted.hot")
        records = cursor.fetchall()
        cursor.close()
        pool.putconn(connection)
        records2=[]
        for i in records:
            records2.append(i[0])
        return records2
    else:
        print("Cant connect")
        raise "ConnectionError"


async def get_all_rising_posted():
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reddit_posted.rising")
        records = cursor.fetchall()
        cursor.close()
        pool.putconn(connection)
        records2=[]
        for i in records:
            records2.append(i)
        return records2
    else:
        print("Cant connect")
        raise "ConnectionError"



async def get_all_hot_posted():
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reddit_posted.hot")
        records = cursor.fetchall()
        cursor.close()
        pool.putconn(connection)
        records2=[]
        for i in records:
            records2.append(i)
        return records2
    else:
        print("Cant connect")
        raise "ConnectionError"

async def insert_rising_post(listpr):
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO reddit_posted.rising(postid, reddit_username) VALUES(%s,%s)",listpr)
        connection.commit()
        cursor.close()
        pool.putconn(connection)
    else:
        print("Cant connect")
        raise "ConnectionError"




async def insert_hot_post(listpr):
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO reddit_posted.hot(postid, reddit_username) VALUES(%s,%s)",listpr)
        connection.commit()
        cursor.close()
        pool.putconn(connection)
    else:
        print("Cant connect")
        raise "ConnectionError"

async def mod_rising_post(modid, action, pid):
    connection = pool.getconn()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE reddit_posted.rising SET mod_id = %s, action = %s, actiondate = %s WHERE postid = %s",(modid,action,time.time(),pid))
        connection.commit()
        cursor.close()
        pool.putconn(connection)
    else:
        print("Cant connect")
        raise "ConnectionError"



async def mod_hot_post(modid, action, pid):
    connection = pool.getconn()
    
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE reddit_posted.hot SET mod_id = %s, action = %s, actiondate = %s WHERE postid = %s",(modid,action,time.time(),pid))
        connection.commit()
        cursor.close()
        pool.putconn(connection)
    else:
        print("Cant connect")
        raise "ConnectionError"



