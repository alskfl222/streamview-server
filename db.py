import os
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()

DBID = os.getenv("MONGODB_ID")
DBPW = os.getenv("MONGODB_PW")
atlas_link = f"mongodb+srv://{DBID}:{DBPW}@info.syvdo.mongodb.net/info?retryWrites=true&w=majority"
dbclient = pymongo.MongoClient(atlas_link, tlsCAFile=certifi.where())
db = dbclient["StreamView"]
