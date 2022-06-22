from pydantic import BaseModel

### using pydanttic BaseModel ,creating an request model

class CityDetails(BaseModel):
    city: str 
    state: str
    pincode: int