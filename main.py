from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session
from schemas import schemas 
from models import models  
from database.db import SessionLocal, engine  
from coordinate.coordinate import Coordinates
import mpu
from datetime import datetime
import logging
# Logging is a Python module in the standard library that provides the facility
#  to work with the framework for releasing log messages from the Python programs.

now =datetime.now()
time = now.strftime("%d_%m_%Y_%H_%M_%S")
file_name = f'logs/log_{time}.txt'
logging.basicConfig(filename=file_name, filemode='a',format='%(asctime)s - %(levelname)s - %(message)s')

# Creating an object
logger = logging.getLogger()
logger.setLevel(logging.INFO)
app = FastAPI()  # creating fastapi server
models.Base.metadata.create_all(engine)
# create_all() function uses the engine object to create all the defined table objects and stores the information in metadata.

# connecting the database
def fetching_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# getting all data from database
@app.get("/getall")
def get_all(db: Session = Depends(fetching_db)):
    logger.info("Requesting all data")
    details = db.query(models.CityDetail).all()
    if details:
        logger.info("Returning all data")
        return details
    else:
        logger.info("No data available")
        return "No data available."

# getting data by id  from database
@app.get("/gettingbyid/{id}")
def get_by_id(id, db: Session = Depends(fetching_db)):
    logger.info(f"Request: id: {id}")
    details = db.query(models.CityDetail).where(models.CityDetail.id == id).first()
    if details:
        logger.info(f"Return: data of id: {id}")
        return details
    else:
        logger.info("request id not available")
        return "request id not available"

# getting all details which are related to given request in search bar which contain a part of city name in table
@app.get("/gettingbysearcha part of city name in table/{city}")
def get_by_search_a_part_of_city_name_table(city, db: Session = Depends(fetching_db)):
    logger.info("request for {city} details")
    details = db.query(models.CityDetail).filter(models.CityDetail.city.like(city + '%')).all()
    if details:
        logger.info("returning for {city} details")
        return details
    else:
        logger.info("no such {city} details")
        return "no such {city} details"

# posting data into database
@app.post("/postingCoordinates")
def createCoordinates(coOrd: schemas.CityDetails, db: Session = Depends(fetching_db)):
    logger.info(f"POST Request: Coordinates")
    city = coOrd.city
    state = coOrd.state
    pincode = coOrd.pincode
    address = city, state, pincode
    location_data = Coordinates(address)  #calling coodinates function which will get the coordinates from given api

    newCordinate = models.CityDetail()  # creating a new row in table  and assigning values to keys respectively
    newCordinate.city = city
    newCordinate.state = state
    newCordinate.pincode = pincode
    newCordinate.longitude = location_data[1]
    newCordinate.latitude = location_data[0]
    try:
        db.add(newCordinate)  # adding row to table
    except Exception as e:
        logger.error(f"DB ERROR: {e}")
    db.commit()  # confirming our changes to database
    logger.info(f"POST Request: Success")
    return newCordinate

# updating data of particular id
@app.put("/updatingCity/{id}")
def updating_city(coOrd: schemas.CityDetails, id, db: Session = Depends(fetching_db)):
    logger.info(f"update request for {id}")
    city = coOrd.city
    state = coOrd.state
    pincode = coOrd.pincode
    address = city, state, pincode

    location_data = Coordinates(address)  #calling coodinates function which will get the coordinates from given api

    updateCoordinate = {}            #updating a row in table  and modifying values to keys respectively
    updateCoordinate["city"] = city
    updateCoordinate["state"] = state
    updateCoordinate["pincode"] = pincode
    updateCoordinate["longitude"] = location_data[1]
    updateCoordinate["latitude"] = location_data[0]

    updating = db.query(models.CityDetail).where(models.CityDetail.id == id).update(updateCoordinate)
    if updating:          # if any rows contains same id as in params  in table
        try:                   
            db.commit()                   #  confirming our changes to database
            logger.info(f"retuning request for {id}")
            return updating, updateCoordinate        
        except Exception as e:
            logger.error(f"DB ERROR: {e}")
    else:  # if no row found
            logger.info("no city with this id " + id)
            return "no city with this id " + id

# deleting data of particular id
@app.delete("/deleteingDetails/{id}")
def delete_coordinates(id, db: Session = Depends(fetching_db)):
    logger.info(f"delete request for {id}")
    deleting = db.query(models.CityDetail).where(models.CityDetail.id == id).delete()
    # deleting if params id is found 

    if deleting:  # if any rows contains same id as in params  in table 
        try:
            db.commit()  #  confirming our changes to database
            logger.info(f"deleted {id}")
            return deleting
        except Exception as e:
            logger.error(f"DB ERROR: {e}")
    else:  # if no row found
        logger.info("no city with this id " + id)
        return "no city with this id " + id


#  deleting all data  in table
@app.delete("/deleteing_all_Details")
def delete_all_coordinates(db: Session = Depends(fetching_db)):
    logger.info("delete request for all data")
    deleting = db.query(models.CityDetail).delete()

    if deleting:  # if any rows are found in table 
        try:
            db.commit()  #  confirming our changes to database
            logger.info(f"deleted all data")
            return "deleted all data in table"
        except Exception as e:
            logger.error(f"DB ERROR: {e}")

    else:  # if no rows found in table
        logger.info("table empty ")
        return "table empty "

#  nearest cities of particular city 
@app.get("/nearestCities/{id}")
def nearest_coordinates(id, db: Session = Depends(fetching_db)):
    logger.info(f"nearestCities request for {id}")
    current = db.query(models.CityDetail).where(models.CityDetail.id == id).first()
    currrent_lat = current.latitude
    current_lon = current.longitude
    getall = db.query(models.CityDetail).all()
    if getall:
        nearestcities = []
        d = []
        for each in getall:
            #  using mpu which is collection of functions , we are using this to calculate distance between 2 coordinates
            dist = mpu.haversine_distance((currrent_lat, current_lon), (each.latitude, each.longitude))
            d.append([(currrent_lat, current_lon), (each.latitude, each.longitude), dist])

            if dist < 100 and each != current:
                nearestcities.append(each)
        logger.info(f" returning nearestCities for {id}")
        return nearestcities
    else:
        logger.info("table empty ")
        return "db empty"

# nearest cities to city which is not in database
@app.get("/nearestCities_of_city_not_in_database")
def nearest_cities(city, state, pincode, db: Session = Depends(fetching_db)):
    logger.info(f"request for nearestCities to  {city}, {state}, {pincode}")
    address = city, state, int(pincode)
    location_data = Coordinates(address)
    currrent_lat = float(location_data[0])
    current_lon = float(location_data[1])
    getall = db.query(models.CityDetail).all()
    if getall:
        nearestcities = []
        d = []
        for each in getall:
            #  using mpu which is collection of functions , we are using this to calculate distance between 2 coordinates
            dist = mpu.haversine_distance((currrent_lat, current_lon), (each.latitude, each.longitude))
            d.append([(currrent_lat, current_lon), (each.latitude, each.longitude), dist])
            if dist < 100:
                nearestcities.append(each)
        if nearestcities:
            logger.info("returning for nearestCities to" + city + state+ pincode)
            return nearestcities
        else:
            logger.info("no such nearest cities")
            return "no such nearest cities"
    else:
        logger.info("table empty ")
        return "db empty"
# THANK YOU 
