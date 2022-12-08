import getpass
import json
import pymongo
import mysql.connector as con
import logging
from utils import *
import os
from decouple import config

'''This class performs various db and local file operations, like connect, save etc'''
class dbOps:

    # set the config path and log activities
    def __init__(self):
        logging.basicConfig(filename = 'scrapper.log',level = logging.INFO, format = '%(asctime)s %(levelname)s %(message)s')


    # method to connect to database
    def __dbConnect__(self,dbname,host = 'localhost'):
        try :
            logging.info(f'connecting to db {dbname}')
            # read config details like username, password for database
            user = config('user')
            password = config('pass')
            if user == None or password == None:
                logging.info('Unable to find config details')
            db = None
            # connect to database
            if  dbname.casefold() == 'mongodb':
                db = pymongo.MongoClient(f"mongodb://{user}:{password}@ac-utrzl6v-shard-00-00.ur7lffv.mongodb.net:27017,ac-utrzl6v-shard-00-01.ur7lffv.mongodb.net:27017,ac-utrzl6v-shard-00-02.ur7lffv.mongodb.net:27017/?ssl=true&replicaSet=atlas-5jlkjl-shard-0&authSource=admin&retryWrites=true&w=majority")
            # for future scope
            elif dbname.casefold() == 'sql':
                db = con.connect(host = host, user = user,passwd = password)
            if db != None:
                logging.info("Connected to Database successfully")
            return db
        except Exception as e:
            logging.error(f'Error connecting to Database {e}')
            return ("Error connecting to Database", e)

    def dbClose(self,db):
        db.close()

    # def addSqlData(self,dbname,data,host = 'localhost'):
    #     pass

    # add data to mongodb
    def addNosqlData(self,dbname,data,host = 'localhost'):
        try:
            dbcon = self.__dbConnect__(dbname,host)

            # select database
            course_db = dbcon['ineuronCourseDB']

            # select collection
            course_collection = course_db['courseList']

            # course_collection.drop()

            # save data to database
            response = course_collection.insert_many(data)
            self.dbClose(dbcon)
            if len(response.inserted_ids) > 0:
                logging.info('Data updated in database')
                return 'Data updated in database'
            else:
                logging.error("Error updating database")
                return 'Error updating database'
        except Exception as e:
            logging.error(f'Error saving data to Database {e}')
            return ("Error saving data to database", e)

    # check details if already exist in database
    def checkDB(self,searchstring):
        try:
            logging.info(f'Searching details in database for course:{searchstring}')
            mydb = self.__dbConnect__('mongodb')['ineuronCourseDB']
            searchstring = cleanString(searchstring)

            mycoll = mydb['courseList']
            courses_exist = []
            for courses in mycoll.find({'searchTerm':{'$regex':searchstring}}):
                courses_exist.append(courses)
            logging.info(f'Courses found with search {len(courses_exist)}')
            return courses_exist

        except Exception as e:
            logging.error(f'Error fetching details from Database {e}')
            return('Error fetching details from Database',e)

    # save to local file
    @staticmethod
    def saveToLocal(data, format = 'json'):
        try:
            logging.info(f'Saving file : {dbOps.localpath}')
            if format == 'json':
                json_data = json.dumps(data,indent=2)
                with open(dbOps.localpath, 'w+') as f:
                    f.write(json_data)
            elif format == 'csv':
                pass
            return 'success'

        except Exception as e:
            logging.error(f'Error saving file to local path {e}')
            return ('Error saving file to local path',e)



