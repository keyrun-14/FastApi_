
### importing required modules

from fastapi import Depends, FastAPI

from sqlalchemy.orm import Session

#importing from local files
from schemas import schemas
from models import models
from database.db import SessionLocal, engine
from coordinate.coordinate import Coordinates


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
    newCordinate.longitude =  locationData[0]
    newCordinate.latitude =  locationData[1] 

    db.add(newCordinate)    ### adding row to table
    db.commit()    ####  confirming our changes to database 
    return newCordinate
 
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
    updateCoordinate["longitude"] =  locationData[0]
    updateCoordinate["latitude"] = locationData[1] 
    

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

##########   THANK YOU  ####################