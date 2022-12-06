import string
import re


'''This module to contains utility methods for variable operations'''
CONFIG_PATH = 'C:\\secrets\\scrapper.json'

# clean string to search better
def cleanString(input_string):
    return re.sub(r'[\W]','',input_string).lower()