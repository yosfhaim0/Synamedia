from flask import Flask, make_response, request
from pymongo import MongoClient

import distanceServer3

app = Flask(__name__)
client = MongoClient(port=27017)
database_name = "synamedia"
db = client[database_name]


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
        return make_response({"error": err}, 500)


@app.route("/distance", methods=['GET'])
def get_distance():
    dist = 0
    source = request.args.get("source")
    destination = request.args.get("destination")
    res = db["Distances"].find_one(
        {'$or': [{'source': source, 'destination': destination}, {'source': destination, 'destination': source}]})
    if res:  # find in database
        dist = res['distance']
        db["Distances"].update_one({'source': source, 'destination': destination}, {'$set': {'hits': res['hits'] + 1}})
        db["Distances"].update_one({'source': destination, 'destination': source}, {'$set': {'hits': res['hits'] + 1}})
        return make_response({"distance": str(dist)}, 200)
    else:  # not found in database
        try:
            dist = distanceServer3.dis(source, destination)
        except:
            return make_response({
                "error": "Something didn't work well with the calculation of the distance between the cities, are you sure the two cities you entered exist?"},
                500)
        db["Distances"].insert_one({'source': source, 'destination': destination, 'distance': dist, 'hits': 1})
        return make_response({"distance": dist}, 200)


@app.route("/popularsearch", methods=['GET'])
def get_popularsearch():
    maxHit = 0
    maxVal = {}
    for i in db["Distances"].find():
        if i.get("hits", False) > maxHit:
            maxHit = i["hits"]
            maxVal = i
    return make_response({"source": maxVal["source"], "destination": maxVal["destination"], "hits": maxVal["hits"]},
                         200)


# to manage json data in a request you have to use the get_json request method.
@app.route("/distance", methods=["POST"])
def post_dista():
    json_details = request.get_json()
    source = json_details['source']
    destination = json_details['destination']
    distance = json_details['distance']
    res = db["Distances"].update_one({'source': source, 'destination': destination}, {'$set': {'distance': distance}},
                                     upsert=True).upserted_id
    hits = db["Distances"].find_one({"_id": res})
    return make_response({'source': source, 'destination': destination,
                          "hits": hits}, 200)


if __name__ == "__main__":
    app.run()

#
