import firebase_admin

from firebase_admin import credentials,firestore

import flask
from flask import abort,jsonify,request,redirect

import json
import requests

from math import sin, cos, sqrt, atan2, radians

app = flask.Flask(__name__)

cred = credentials.Certificate("lets-food-admin-key.json")
firebase_admin.initialize_app(cred)
store = firestore.client()

@app.route('/addRestaurant',methods=['POST'])

def addRestaurant():
    data = request.get_json(force=True)
    dit = {}
    dit['name'] = data.get("name")
    dit['mobile'] = data.get("mobile")
    dit['address'] = data.get("address")
    dit['location'] = {"lat" : data.get("lat"),"long":data.get("lng")}
    dit['type'] = data.get("typ")
    dit['rest_id'] = data.get("rest_id")
    dit['imageURL'] = data.get("imageURL")
    dit['createdAt'] = firestore.SERVER_TIMESTAMP

    store.collection("RESTAURANTS").add(dit)

    return jsonify({"Response":200, })

@app.route('/search/id',methods=['POST'])

def searchRestaurant():
    data = request.get_json(force=True)
    rest_id = data.get("rest_id")
    doc = store.collection("RESTAURANTS").where("rest_id","==",rest_id).stream()
    rest_lst = []
    for docs in doc:
        rest_lst.append(docs.to_dict())
    
    return jsonify({"Response":200, "Rest_list" : rest_lst})

@app.route('/search/coordinates',methods=['POST'])
def searchByCor():
    data = request.get_json(force=True)
    myLat = data.get("myLat")
    myLong = data.get("myLong")
    r = data.get("range")

    allRestsData = store.collection("RESTAURANTS").stream()
    nearByRest = []

    R = 6373.0

    for rest in allRestsData:
        try:
            dit = rest.to_dict()
            rLat = float(dit.get('location').get('lat'))
            rLong = float(dit.get('location').get('long'))
            #print(rLat,rLong)

            lat1 = radians(rLat)
            lon1 = radians(rLong)
            lat2 = radians(myLat)
            lon2 = radians(myLong)
            
            dlon = lon2 - lon1
            dlat = lat2 - lat1


            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c

            if distance <= r:
                nearByRest.append(dit)
        except:
            print("Wrong code")

    return jsonify({"Response":200,"rests_list":nearByRest})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=False)
