from dbOperations import dbOps
from utils import *

db = dbOps(CONFIG_PATH)
res = db.fetchCourseDetails('full')
print(res)
