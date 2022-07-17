from flask import Flask, make_response, request
# from api_constants import mongodb_password
from pymongo import MongoClient

import distanceServer3

app = Flask(__name__)

client = MongoClient(port=27017)
db = client["synamedia"]

database_name = "synamedia"


# DB_URI="mongodb+srv://synamedia:<password>@cluster0.rar8h.mongodb.net/?retryWrites=true&w=majority
# mongodb_password,database_name)
#
# app.config["MONGODB_HOST"]=DB_URI
# db=MongoEngine()

# db.init_app(app)

@app.route("/hello", methods=['GET'])
def get_hello():
    return make_response({}, 200)


# todo
@app.route("/health", methods=['GET'])
def get_health():
    try:
        db = client["synamedia"]
        x = db["Distances"]
        return make_response({"Ok": "123"}, 200)
    except Exception as err:
        return make_response({"Error": err}, 500)


@app.route("/distance", methods=['GET'])
def get_distance():
    source = request.args.get("source")
    destination = request.args.get("destination")
    res = db["Distances"].find_one(
        {'$or': [{'source': source, 'destination': destination}, {'source': destination, 'destination': source}]})
    if res:  # find in database
        c = res['distance']
        # oldhit=res['hits']
        db["Distances"].update_one({'source': source, 'destination': destination}, {'$set': {'hits': res['hits'] + 1}})
        return make_response({"distance": str(c)}, 200)
    else:  # not found
        res = distanceServer3.dis(source, destination)
        db["Distances"].insert_one({'source': source, 'destination': destination, 'distance': res, 'hits': 1})
        return make_response({"distance": res}, 200)


@app.route("/popularsearch", methods=['GET'])
def get_popularsearch():
    db["Distances"].aggregate()


if __name__ == "__main__":
    app.run()

#
