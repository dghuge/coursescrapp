import logging

from scrapperUtils import scrapper
from dbOperations import dbOps
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from utils import *
import requests

app = Flask(__name__)

# variable to store final extracted data
data_extract = ''


# Display homepage
@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('home.html')


# Display details
@app.route('/details', methods=['GET', 'POST'])
@cross_origin()
def details():

    # query to filter courses
    searchstring = request.form['content']

    # url to scrap course details from
    url = 'https://www.ineuron.ai'

    # creating instance of scrapper and db class to use its methods
    sc = scrapper()

    # CONFIG PATH to store db credential and local file path for save
    db = dbOps(CONFIG_PATH)

    # check if course details already exist in scrapped database
    db_course_data = db.checkDB(searchstring)
    if len(db_course_data) > 0:
        data_extract = db_course_data
    else:
        # if data doesn't exist in database then start scrapping
        url_data = sc.getUrlData(url, searchstring)

        # filter data based on tag
        tag_data = sc.getTagContent(url_data, 'script', {"id": "__NEXT_DATA__"})

        # parsing data to get course list
        #course_list = sc.ineuronCourseListParser(tag_data)

        # find list of details for all courses
        data_extract = sc.ineuronCourseDetails(tag_data)
        if len(data_extract) == 0:
            return render_template('message.html', message='Unable to find details for given string')
        else:
            # add scrapped data to database
            response = db.addNosqlData('mongodb', data_extract)
    return render_template('details.html', data_extract=data_extract)


# save json file to local path
@app.route('/details/savejson', methods=['POST'])
@cross_origin()
def saveJson():
    try:
        res = dbOps.saveToLocal(data_extract)
        if res == 'success':
            return render_template('message.html', message='file saved to local drive')
        else:
            return render_template('message.html', message='unable to save file')
    except Exception as e:
        logging.error(f'Unable to save data to local file {e}')
        return render_template('message.html', message = 'Unable to save data to local file')


if __name__ == '__main__':
    app.run(debug=True)
