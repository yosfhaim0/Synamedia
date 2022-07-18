from flask import Flask, make_response, request
from pymongo import MongoClient

import distanceCalculator

app = Flask(__name__)
client = MongoClient(port=27017)
database_name = "synamedia"
db = client[database_name]


@app.route("/hello", methods=['GET'])
def get_hello():
    return make_response({}, 200)


# get the distance in KM between a source and destination
@app.route("/distance", methods=['GET'])
def get_distance():
    dist = 0
    try:
        source = request.args.get("source")
        destination = request.args.get("destination")
        source, destination = sortName(source, destination)
    except TypeError:
        return make_response(
            {"error": "The format should be as follows: /distance?source=YourSource&destination=YourDestination"}, 500)
    get_health()
    res = find_in_db(source, destination)
    if res:  # find in database
        dist = res['distance']
        db["Distances"].update_one({'source': source, 'destination': destination}, {'$set': {'hits': res['hits'] + 1}})
        return make_response({"distance": str(dist)}, 200)
    else:  # not found in database
        try:
            dist = distanceCalculator.distance_between_cities(source, destination)
        except:
            return make_response({
                "error": "Something didn't work well with the calculation of the distance between the cities, are you sure the two cities you entered exist?"},
                500)
        insert_one(source, destination, dist)
        return make_response({"distance": dist}, 200)


# The /health API is responsible for determining the status of the connection to the DB
@app.route("/health", methods=['GET'])
def get_health():
    try:
        db = client[database_name]
        db["Distances"]
        return make_response({}, 200)
    except:
        return make_response({"error": "the connection to mongo is unavailable"}, 500)


# get the most popular search and number of hits,
# return the last one popular search that appears in collection
@app.route("/popularsearch", methods=['GET'])
def get_popularsearch():
    max_hit, max_val = 0, {}
    get_health()
    for i in db["Distances"].find():
        if i.get("hits", False) > max_hit:
            max_hit, max_val = i["hits"], i
    if max_val == {}:
        return make_response({"error": "No valid result returned, probably the collection is empty"}, 500)
    return make_response({"source": max_val["source"], "destination": max_val["destination"], "hits": max_val["hits"]},
                         200)


# allow ingesting a pair
@app.route("/distance", methods=["POST"])
def post_distance():
    try:
        json_details = request.get_json()
        source = json_details['source']
        destination = json_details['destination']
        source, destination = sortName(source, destination)
        distance = json_details['distance']
    except KeyError:
        return make_response({
            "error": 'your json file format: {"source": "YourSource", "destination": "YourDestination", "distance": Yourdistance} and '},
            500)
    except Exception:
        return make_response({"error": "you should add legal json file to the body post request"}, 500)
    get_health()
    res = find_in_db(source, destination)
    if res:
        db["Distances"].update_one({'source': source, 'destination': destination, "hits": res["hits"]},
                                   {'$set': {'distance': distance}})
        return make_response({'source': source, 'destination': destination,
                              "hits": res['hits']}, 200)
    else:
        db["Distances"].insert_one(
            {'source': source, 'destination': destination, 'distance': distance, 'hits': 1})
        return make_response({'source': source, 'destination': destination,
                              "hits": 1}, 200)


# in the database always source < destination
def sortName(source, destination):
    if source <= destination:
        return source, destination
    else:
        return destination, source


def find_in_db(source, destination):
    return db["Distances"].find_one({'source': source, 'destination': destination})


def insert_one(source, destination, dist, hits=1):
    db["Distances"].insert_one({'source': source, 'destination': destination, 'distance': dist, 'hits': hits})


if __name__ == "__main__":
    app.run()
