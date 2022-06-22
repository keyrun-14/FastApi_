
### importing required modules

from fastapi import Depends, FastAPI,Request

from sqlalchemy.orm import Session

#importing from local files
from schemas import schemas
from models import models
from database.db import SessionLocal, engine
from coordinate.coordinate import Coordinates

import mpu

app = FastAPI()  ## creating fastapi server

models.Base.metadata.create_all(engine)   
###  create_all() function uses the engine object to create all the defined table objects and stores the information in metadata.


##### connecting the database
def fetching_Db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### getting all data from database
@app.get("/getall")
def get_all( db :Session = Depends(fetching_Db)):
        details = db.query(models.CityDetail).all()
        return details


###     getting data by id  from database
@app.get("/gettingbyid/{id}")
def get_by_id( id,db :Session = Depends(fetching_Db)):
        details = db.query(models.CityDetail).where(models.CityDetail.id==id).first()
        return details

######     getting city details by id 
@app.get("/gettingbysearch/{city}")
def get_by_search( city,db :Session = Depends(fetching_Db)):
        details = db.query(models.CityDetail).filter(models.CityDetail.city.like(city+'%')).all()
        return details

###     posting data into database
@app.post("/postingCoordinates")
def createCoordinates(coOrd: schemas.CityDetails, db :Session = Depends(fetching_Db)):  
    city = coOrd.city
    state = coOrd.state
    pincode = coOrd.pincode
    address=city,state,pincode
 
    locationData = Coordinates(address)  ###calling coodinates function which will get the coordinates from given api

    newCordinate = models.CityDetail() ### creating a new row in table  and assigning values to keys respectively

    newCordinate.city = city
    newCordinate.state = state
    newCordinate.pincode = pincode
    newCordinate.longitude =  locationData[1]
    newCordinate.latitude =  locationData[0] 

    db.add(newCordinate)    ### adding row to table
    db.commit()    ####  confirming our changes to database 
    return newCordinate,locationData
 
 ####     updating data of particular id
@app.put("/updatingCity/{id}")
def updating_city(coOrd: schemas.CityDetails,id,db:Session=Depends(fetching_Db)):
    city = coOrd.city
    state = coOrd.state
    pincode = coOrd.pincode
    address=city,state,pincode
 
    locationData = Coordinates(address)   ###calling coodinates function which will get the coordinates from given api

    updateCoordinate ={}    ####updating a row in table  and modifying values to keys respectively
    updateCoordinate["city"] = city
    updateCoordinate["state"] = state
    updateCoordinate["pincode"]= pincode
    updateCoordinate["longitude"] =  locationData[1]
    updateCoordinate["latitude"] = locationData[0] 
    

    updating=db.query(models.CityDetail).where(models.CityDetail.id==id).update(updateCoordinate)
    if updating:   ### if any rows contains same id as in params  in table 
        db.commit()    ####  confirming our changes to database 
        return updating,updateCoordinate
    else:     ### if no row found
        return "no city with this id "+id


 ####    deleting data of particular id
@app.delete("/deleteingDetails/{id}")
def deleteCoordinates(id,db:Session=Depends(fetching_Db)):
    deleting=db.query(models.CityDetail).where(models.CityDetail.id==id).delete()
    ## deleting if params id is found 

    if deleting:  ### if any rows contains same id as in params  in table 
        db.commit()   ####  confirming our changes to database 
        print(deleting)
        return deleting
    else:  ### if no row found
        return "no city with this id "+id

 ####  deleting all data  in table
@app.delete("/deleteing_all_Details")
def delete_All_Coordinates(db:Session=Depends(fetching_Db)):

    deleting=db.query(models.CityDetail).delete()

    if deleting:  ### if any rows are found in table 
        db.commit()   ####  confirming our changes to database 
        return "deleted all data in table"

    else:   ### if no rows found in table 
        return "table empty "

        
###  nearest cities of particular city 
@app.get("/nearestCities/{id}")
def nearestCoordinates(id,db:Session=Depends(fetching_Db)):
    current=db.query(models.CityDetail).where(models.CityDetail.id==id).first()
    currrent_lat=current.latitude
    current_lon=current.longitude
    getall=db.query(models.CityDetail).all()
    nearestcities=[]
    d=[]
    for each in getall:
        ######  using mpu which is collection of functions , we are using this to calculate distance between 2 coordinates
        dist = mpu.haversine_distance((currrent_lat, current_lon), (each.latitude,each.longitude))
        d.append([(currrent_lat, current_lon), (each.latitude,each.longitude),dist])
       
        if dist<100 and each!=current:
            nearestcities.append(each)
    return nearestcities


##### nearest cities to city which is not in database
@app.get("/nearestCities_of_city_not_in_database")
def nearestCities(city,state,pincode ,db:Session=Depends(fetching_Db)):
    
    address=city,state,int(pincode)
    locationData = Coordinates(address)
    currrent_lat=float(locationData[0])
    current_lon=float(locationData[1])
    getall=db.query(models.CityDetail).all()
    nearestcities=[]
    d=[]
    for each in getall:
        ######  using mpu which is collection of functions , we are using this to calculate distance between 2 coordinates
        dist = mpu.haversine_distance((currrent_lat, current_lon), (each.latitude,each.longitude))
        d.append([(currrent_lat, current_lon), (each.latitude,each.longitude),dist])
        if dist<100:
            nearestcities.append(each)
    return nearestcities


# from math import sin, cos, sqrt, atan2, radians

# # approximate radius of earth in km
# R = 6373.0

# # lat1 = radians(52.2296756)
# # lon1 = radians(21.0122287)
# # lat2 = radians(52.406374)
# # lon2 = radians(16.9251681)
# # Point one
# lat1 = radians(28.6139)
# lon1 =  radians(77.2090)

# # Point two
# lat2 = radians(17.6868)
# lon2 = radians(83.2185)

# dlon = lon2 - lon1
# dlat = lat2 - lat1

# a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
# c = 2 * atan2(sqrt(a), sqrt(1 - a))

# distance = R * c

# print("Result:", distance)
# print("Should be:", 278.546, "km")
##########   THANK YOU  ####################