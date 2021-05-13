import firebase_admin
from firebase_admin import auth,credentials,firestore
from math import sin, cos, sqrt, atan2, radians
from flask import abort, jsonify, request
import flask
import json
from flask import Flask

#--------------------------FIREBASE INITIALIZATION----------------------#
cred = credentials.Certificate("LETS-GO.json")
firebase_admin.initialize_app(cred)
store=firestore.client()
#-----------------------------------------------------------------------#


#--------------------------FLASK INITIALIZATION-------------------------#
app = flask.Flask(__name__)
#-----------------------------------------------------------------------#
@app.route("/sign",methods=['POST'])
def usersignup():
    data=request.get_json(force=True)
    msg=""
    id=""
    try:
        user = auth.create_user(
        email=data.get("useremail"),
        email_verified=False,
        password=data.get("userpassword"),
        disabled=False)
        id = user.uid
        return jsonify("Successfully created new user")
    except:
        return jsonify("User already there")

@app.route("/passenger",methods=['POST'])
def passdetails():
    data=request.get_json(force=True)

    dit={}
    dit["name"] = data.get("name")
    dit["Age"] = data.get("age")
    dit["contact"] = data.get("contact")
    dit["Address"] = {"slat":data.get("slat"),"slong":data.get("slong")}

    store.collection("PASSENGER").document(id).set(dit) 

    return jsonify({"Response:":200})

@app.route("/driver",methods=['POST'])
def driverdetails():
    data=request.get_json(force=True)
    dit={}
    dit["Name"] = data.get("dname")
    dit["AGE"] = data.get("dage")
    dit["Contact"] = data.get("dnumber")
    dit["Start location"] = {"startplace":data.get("startplace"),"dslat":data.get("dslat"),"dslong":data.get("dslong")}
    dit["Max distance"] = {"finalplace":data.get("finalplace"),"lat":data.get("drlat"),"long":data.get("drlong")}
    dit["Car Number"] = data.get("carnumber")
    dit["rating"] = 0

    store.collection("DRIVERS").add(dit)

    return jsonify({"Response:":200})

@app.route("/searching",methods=['GET'])
def searchdriver():
    data=request.get_json(force=True)
    count=0
    dit={}
    driver_details={}
    dit1={}
    print("Pass")
    docs=store.collection("PASSENGER").stream()
    for doc in docs:
        if doc.to_dict().get("name") == data.get("Passname"):
            # print("User successfully found")
            ID = doc.id
            dit[ID] = doc.to_dict()
            break

    startlat = dit[ID]["Address"]["slat"]
    startlong = dit[ID]['Address']['slong']
  
    R = 6373.0

    lat1 = startlat
    lon1 = startlong
    lat2 = data.get("destlat")
    lon2 = data.get("destlong")

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distancetravelled = R * c

    

    docs = store.collection("DRIVERS").stream()
    for doc in docs:
        ID = doc.id
        dit1[doc.id] = doc.to_dict()
    
        driverstartlat = dit1[ID]["Start location"]["dslat"]
        driverstartlong = dit1[ID]["Start location"]["dslong"]
        driverfinallat = dit1[ID]["Max distance"]["lat"]
        driverfinallong = dit1[ID]["Max distance"]["long"]

        lat1 = radians(driverstartlat)
        lon1 = radians(driverstartlong)
        lat2 = radians(startlat)
        lon2 = radians(startlong)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        pickupdistance = R * c


        lat1 = radians(driverstartlat)
        lon1 = radians(driverstartlong)
        lat2 = radians(driverfinallat)
        lon2 = radians(driverfinallong)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        driverdistance = R * c

        lat1 = radians(driverstartlat)
        lon1 = radians(driverstartlong)
        lat2 = radians(data.get("destlat"))
        lon2 = radians(data.get("destlong"))

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        traveldistance = R * c

        if pickupdistance <= driverdistance:
            print("Your nearby driver has been notified..waiting for his approval")
            if traveldistance <= driverdistance:
                print("Driver found....details are as follows")
                count+=1
                driver_details[ID]=dit1[ID]
               # return jsonify(dit1)
            else:
                print("No driver found for taking you to your destination")
        else:
            print("Out of range")
    return jsonify(driver_details)

@app.route("/rate",methods=['POST'])
def rating():
    data=request.get_json(force = True)
    r = data.get("rating")
    driverid = data.get("id")
    print("Thank you for travelling with us..")
    docs = store.collection("DRIVERS").stream()
    driverdit={}
    drname = data.get("drivername")
    for driver in docs:
        if driver.to_dict().get("dname") == drname:
            driverdit[driver.id] = driver.to_dict()
    driverdit["rating"] = r

    store.collection("DRIVERS").document(driverid).update(driverdit)

    return jsonify(driverdit)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port="5003",debug=False)