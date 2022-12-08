#from flask import Flask, render_template, request,jsonify
#from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from dbOperations import  dbOps
from utils import *
#from urllib.request import urlopen as uReq, Request
import json
import logging
import getpass

'''This class provide various methods to scrap data'''
class scrapper:

    PARSER_KV = {
        "html"  : "html.parser",
        "html5" : "html5lib",
        "xml"   : "lxml"
    }

    # set db instance and search query to use throught the methods
    def __init__(self):
        self.db = dbOps()
        self.searchQuery = ''

        # log all activities inside the class
        logging.basicConfig(filename = 'scrapper.log',level = logging.INFO, format = '%(asctime)s %(levelname)s %(message)s')
        logging.info(f'Username : {getpass.getuser()}')

    # scrap data from url in format html,html5,xml
    def getUrlData(self,url,searchstring = '',encoding = 'utf-8',format = 'html'):
        try:
            logging.info(f'Getting url data...{url}')

            # form the search query to filter data later
            query = cleanString(searchstring)
            self.searchQuery = re.compile(r'('+query+')')

            # get data from url/website
            req = requests.get(url)
            logging.info(f'Request status...{req.status_code}')
            if req.status_code == 202 or req.status_code == 200:
                # parse the data
                req.encoding = encoding
                req_formatted = bs(req.content,scrapper.PARSER_KV[format])
                return req_formatted
            else:
                logging.error(f'Unable to reach url {req.reason}')

        except Exception as e:
            logging.error(f'Error getting site content {e}')
            return (f'Error getting site content', e)

    # get content inside a tag and filter based on id if required
    def getTagContent(self,url_content,tag,filter_id=None):
        try:
            logging.info(f'searching content for tag...{tag}')
            if filter_id == None:
                return url_content.find(tag)
            else:
                return url_content.find(tag,filter_id)
        except Exception as e:
            logging.error(f'Error retrieving tag contents {e}')
            return ('Error retrieving tag contents',e)


    # returns the list of course name
    def ineuronCourseListParser(self,all_data):
        try:
            courseList = {}
            json_data = json.loads(all_data.text)
            categories = json_data.get('props').get('pageProps').get('initialState').get('init').get('categories')
            if categories is not None:
                logging.info('extracting course categories...')
                for category in categories.values():
                    categoryName = category['title']
                    subcategories = category['subCategories']
                    subcategoriesList = []
                    for subcategory in subcategories.values():
                        subcategoriesList.append(subcategory['title'])
                    courseList[categoryName] = subcategoriesList
            else:
                logging.info(f'unable to find course categories')
            return courseList
        except Exception as e:
            logging.info(f'Error fetching course list {e}')
            return ('Error fetching course list', e)


    # returns the list of courses with details with each course details in json format
    def ineuronCourseDetails(self,all_data):
        try:
            json_data = json.loads(all_data.text)
            puncutations = string.punctuation
            res_details = []
            all_courses_details = json_data.get('props').get('pageProps').get('initialState').get('init').get('courses')
            if all_courses_details is not None:
                logging.info('start scrapping')
                extracted_details = {}
                for course_name,course_details in all_courses_details.items():
                    logging.info(f'extracting details for {course_name}...')
                    search_term = cleanString(course_name)
                    course_data = None
                    if ( self.searchQuery != '' and self.searchQuery.search(search_term)):
                        course_data = self.formatCourse(course_name,course_details,search_term)
                    elif self.searchQuery == '':
                        course_data = self.formatCourse(course_name,course_details,search_term)
                    if course_data is not None:
                        res_details.append(course_data)
                logging.info(f'extraction completed')
            return res_details

        except Exception as e:
            logging.error(f'Error finding courses detail {e}')
            return ('Error finding courses detail', e )

    # returns data formatted
    def formatCourse(self,course_name, course_details,search_term):
        details = {}
        base_link = 'https://ineuron.ai/course/'
        details['courseName']  = course_name

        # form a search term to search course in Database
        details['searchTerm']  = search_term
        details['description'] = course_details.get('description')
        course_meta = course_details.get('courseMeta')
        if course_meta is not None:
            course_overview = course_meta[0].get('overview')
            if course_overview is not None:
                details['toLearn']      = course_overview.get('learn')
                details['requirements'] = course_overview.get('requirements')
                details['features']     = course_overview.get('features')

        details['mode'] = course_details['mode']

        time_details = course_details.get('classTimings')
        if time_details is not None:
            time_data = {'timings'      : time_details.get('timings'),
                         'startDate'    : time_details.get('startDate'),
                         'doubtClearing': time_details.get('doubtClearing')}
            details['timeDetails'] = time_data

        details['price'] = course_details.get('pricing')

        instructor_details = course_details.get('instructorsDetails')
        instructors = []
        for instructor_detail in instructor_details:
            instructor = {'name'       : instructor_detail.get('name'),
                          'social'     : instructor_detail.get('social'),
                          'description': instructor_detail.get('description')}
            instructors.append(instructor)
        details['instructors'] = instructors
        details['courseLink'] = base_link + course_name.replace(' ', '-')
        return details.copy()








