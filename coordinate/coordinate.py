import requests
import urllib.parse
#######  getting cordinates using this api  when function calls for particular input.
def Coordinates(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(str(address)) + '?format=json'
    response_location = requests.get(url).json()
    a=[response_location[0]["lat"] , response_location[0]["lon"]]
    return a
# print(Coordinates("srikakulam, ANDHRA PRADESH,532185"))