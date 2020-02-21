from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['parse_hh_sj']
hh_collection = db.hh_collection

def db_save(obj):
    hh_collection.insert_many(obj)
    objects = hh_collection.find()

    for obj in objects:
        pprint(obj)

def find_wish_salary(wish_salary):

    test_find = hh_collection.find( { '$or': [ { 'min': { '$gte' : wish_salary } }, { 'max': {'$gte' :wish_salary} } ] } )

    for test in test_find:
        pprint(test)

def update_vacancies(obj):
    link = obj['link']

    exist = hh_collection.find({'link' : link})
    if exist.count() == 0:
        hh_collection.insert_one(obj)

